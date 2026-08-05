import maya.cmds as cmds
import maya.mel as mel

##################################################################################
# jlr_sort_attributes.py - Python Script
##################################################################################
# Description:
# Tools for sort user defined attributes in the channel box.
# Creates two menu item commands in the Main Modify Menu, Channel Box Edit Menu and Channel Box Popup Menu.
#
# Author: Juan Lara.
##################################################################################
# Install:
# 1- Copy this script file to your scripts directory.
# 2- In the userSetup.py add the following lines:
#
# import maya.cmds as cmds
# import jlr_sort_attributes
#
# cmds.evalDeferred('jlr_sort_attributes.create_menu_commands()')
#
##################################################################################
# How to use "Move Attributes Up" or "Move Attributes Down":
#
# Select one or more user-defined attributes in the channel box.
# Click on "Move Attributes Up" to move the selected attributes one position up.
# Or click on "Move Attributes down" to move the selected attributes one position down.
#
# --------------------------------------------------------------------------------
# How to use Copy, Cut and Paste Attributes:
#
# First select an object and in the channel box, select one or more user-defined attributes.
# Click on "Copy attributes" to copy the selected attributes.
# Or click on 'Cut attributes' to move the selected attributes.
# Finally select the object where you want to copy or move the previously selected attributes
# and click on "Paste attributes".
##################################################################################

#########################################
# Global Variables
#########################################

__jlr_copy_data = None
__jlr_copy_mode = None


##############################################
# Menus Items
##############################################

def create_menu_commands():
    """
    Create the menu commands.
    Move Up: Move the selected attributes one position up.
    Move Down: Move the selected attributes one position down.
    """
    channels_menu = 'ChannelBoxLayerEditor|MainChannelsLayersLayout|ChannelsLayersPaneLayout|ChannelBoxForm|menuBarLayout1|menu2'
    edit_menu = 'ChannelBoxLayerEditor|MainChannelsLayersLayout|ChannelsLayersPaneLayout|ChannelBoxForm|menuBarLayout1|menu3'
    channel_box_popup = 'ChannelBoxLayerEditor|MainChannelsLayersLayout|ChannelsLayersPaneLayout|ChannelBoxForm|menuBarLayout1|frameLayout1|mainChannelBox|popupMenu1'
    main_modify_menu = 'MayaWindow|mainModifyMenu'

    mel.eval('generateChannelMenu {} 0;'.format(channels_menu))
    mel.eval('generateCBEditMenu {} 0;'.format(edit_menu))
    mel.eval('generateChannelMenu {} 1;'.format(channel_box_popup))
    mel.eval('ModObjectsMenu {};'.format(main_modify_menu))

    channels_menuitems = [
        {'name': 'jlr_channels_menuDivider', 'label': '', 'command': None},
        {'name': 'jlr_unlock_trs', 'label': 'Unlock Transformations', 'command': unlock_trs_attributes},
    ]

    edit_menuitems = [
        {'name': 'jlr_options_menuDivider', 'label': '', 'command': None},
        {'name': 'jlr_add_divider', 'label': 'Add Divider', 'command': add_divider_attribute},
        {'name': 'jlr_sort_menuDivider', 'label': 'Sort Attributes', 'command': None},
        {'name': 'jlr_cbf_attrMoveUp', 'label': 'Move Attributes Up', 'command': move_up_attribute},
        {'name': 'jlr_cbf_attrMoveDown', 'label': 'Move Attributes Down', 'command': move_down_attribute},
        {'name': 'jlr_edit_menuDivider', 'label': '', 'command': None},
        {'name': 'jlr_cbf_attrCut', 'label': 'Cut Attributes', 'command': cut_attribute},
        {'name': 'jlr_cbf_attrCopy', 'label': 'Copy Attributes', 'command': copy_attribute},
        {'name': 'jlr_cbf_attrPaste', 'label': 'Paste Attributes', 'command': paste_attribute},
    ]

    remove_ui_item_menu(['jlr_divider'])
    remove_ui_item_menu([item['name'] for item in edit_menuitems])

    add_commands_to_menu(channels_menuitems, channels_menu)
    add_commands_to_menu(edit_menuitems, edit_menu)
    add_commands_to_menu(channels_menuitems, channel_box_popup)
    add_commands_to_menu(edit_menuitems, channel_box_popup)
    add_commands_to_menu(edit_menuitems, main_modify_menu)


def remove_ui_item_menu(name_list):
    """
    It removes command menu items from maya UI.
    :param name_list: list with the name of UI items to remove.
    """
    for name in name_list:
        for item in cmds.lsUI():
            if item.endswith(name):
                cmds.deleteUI(item)


def add_commands_to_menu(commands, menu):
    """
    It adds a new menu items to a menu.
    :param commands: list of dictionaries with the name, label and command of menu item.
    :param menu: menu object where the items will be created.
    """

    for item in commands:
        name = item['name']
        label = item['label']
        command = item['command']

        if '_menuDivider' in name:
            name = '{}_{}'.format(menu.split('|')[-1], name)
            cmds.menuItem(name, parent=menu, divider=True, dividerLabel=label)

        else:
            name = '{}_{}'.format(menu.split('|')[-1], name)
            cmds.menuItem(name, parent=menu, label=label, command=command)


#########################################
# Attribute methods
#########################################

def copy_attr(node_source, node_target, attr_name, move=False):
    """
    Copy or move a existing user defined attribute between nodes.
    Copy the source attribute connections to the new attribute.
    If the attribute is copied and has connections, these will be connected through a pairBlend node in order
    to maintain the old and new connections.
    If the attribute can not be moved returns None.
    :param node_source: String. Object with the user defined attribute.
    :param node_target: String. Object will receive the user defined attribute.
    :param attr_name: String. Name of the attribute to be copied.
    :param move: Boolean. Indicate if the attribute must be copied or moved.
    :return: String. The new attribute full name (node.attr).
    """
    node_source = str(node_source)
    node_target = str(node_target)

    if not cmds.attributeQuery(attr_name, node=node_source, exists=True):
        cmds.warning('The attribute {} does not exist in {}'.format(attr_name, node_source))
        return None

    source_attr_full = '{}.{}'.format(node_source, attr_name)

    # Get source attribute info.
    attr_data = get_attr_info(node_source, attr_name)
    if not attr_data:
        return None

    source_value = _safe_get_attr(source_attr_full)
    source_is_locked = cmds.getAttr(source_attr_full, lock=True)
    source_is_compound = _is_compound(node_source, attr_name)
    source_connections = get_attr_connections(node_source, attr_name)

    # If attribute is a Compound, read the children attributes info.
    source_child_info = dict()
    source_child_connections = dict()
    if source_is_compound:
        for child in _get_children(node_source, attr_name):
            source_child_info[child] = get_attr_info(node_source, child)
            source_child_connections[child] = get_attr_connections(node_source, child)

    # Creates a list with all attributes connected to source attribute and its lock status.
    l_check = list()
    l_check.extend(source_connections['inputs'])
    l_check.extend(source_connections['outputs'])
    if source_is_compound:
        for child in _get_children(node_source, attr_name):
            l_check.extend(source_child_connections[child]['inputs'])
            l_check.extend(source_child_connections[child]['outputs'])

    l_locked = [[attr_full, cmds.getAttr(attr_full, lock=True)] for attr_full in l_check]

    # Unlock all attributes connected
    for attr_full in l_check:
        _unlock_attr(attr_full)

    # If move is True, delete the source attribute.
    if move:
        if cmds.getAttr(source_attr_full, lock=True):
            _unlock_attr(source_attr_full)
        cmds.deleteAttr(source_attr_full)

    # Create the attribute
    create_attr(node_target, attr_data)

    # If attribute is a Compound, the children attributes are created
    if source_is_compound:
        for child_key in sorted(source_child_info.keys()):
            create_attr(node_target, source_child_info[child_key])

    new_attr_full = '{}.{}'.format(node_target, attr_name)

    # Copy the value
    _safe_set_attr(new_attr_full, source_value)

    # Copy the lock status
    cmds.setAttr(new_attr_full, lock=source_is_locked)

    # Connect the attributes
    connect_attr(new_attr_full, **source_connections)

    # If attribute is a Compound, the children attributes are connected.
    if source_is_compound:
        child_names = sorted(source_child_connections.keys())
        for child_name in child_names:
            child_attr_full = '{}.{}'.format(node_target, child_name)
            connect_attr(child_attr_full, **source_child_connections[child_name])

    # Lock all attributes connected locked previously.
    for attr_full, is_locked in l_locked:
        if is_locked:
            _lock_attr(attr_full)

    return new_attr_full


def _safe_get_attr(attr_full):
    """Safely get attribute value, returns None on failure."""
    try:
        return cmds.getAttr(attr_full)
    except Exception:
        return None


def _safe_set_attr(attr_full, value):
    """Safely set attribute value."""
    if value is None:
        return
    try:
        attr_type = cmds.getAttr(attr_full, type=True)
        if attr_type in ['string']:
            cmds.setAttr(attr_full, value, type='string')
        elif attr_type in ['double3', 'float3']:
            if isinstance(value, (list, tuple)) and len(value) >= 3:
                cmds.setAttr(attr_full, *value[0] if isinstance(value[0], (list, tuple)) else value)
        else:
            cmds.setAttr(attr_full, value)
    except Exception:
        pass


def _unlock_attr(attr_full):
    """Unlock an attribute."""
    try:
        cmds.setAttr(attr_full, lock=False)
    except Exception:
        pass


def _lock_attr(attr_full):
    """Lock an attribute."""
    try:
        cmds.setAttr(attr_full, lock=True)
    except Exception:
        pass


def _is_compound(node, attr_name):
    """Check if attribute is compound."""
    try:
        children = cmds.attributeQuery(attr_name, node=node, listChildren=True)
        return children is not None and len(children) > 0
    except Exception:
        return False


def _get_children(node, attr_name):
    """Get children attribute names of a compound attribute."""
    try:
        children = cmds.attributeQuery(attr_name, node=node, listChildren=True)
        return children or []
    except Exception:
        return []


def _get_parent_attr(node, attr_name):
    """Get parent attribute name if any."""
    try:
        parent = cmds.attributeQuery(attr_name, node=node, listParent=True)
        return parent[0] if parent else None
    except Exception:
        return None


def create_attr(node, attr_data):
    """
    This method creates a new attribute in a node.
    If the node already has an attribute with the same name, the new attribute will not be created.
    :param node: String node name.
    :param attr_data: dictionary with the necessary data to create the attribute.
    """
    attr_name = attr_data['longName']
    if cmds.attributeQuery(attr_name, node=node, exists=True):
        cmds.warning('The attribute {} already exist in {}.'
                     'Can not create a new attribute with the same name'.format(attr_name, node))
    else:
        # Build kwargs without 'type' key (use dataType or attributeType)
        kwargs = {k: v for k, v in attr_data.items()}
        # enumName must be a string for cmds.addAttr
        if 'enumName' in kwargs and isinstance(kwargs['enumName'], dict):
            # Convert ordered dict to colon-separated string
            kwargs['enumName'] = ':'.join(str(k) for k in kwargs['enumName'].keys())
        cmds.addAttr(node, **kwargs)


def connect_attr(attribute, inputs=None, outputs=None):
    """
    It connects an attribute to passed inputs and outputs.
    :param attribute: Attribute full name (node.attr).
    :param inputs: list of input attribute full names.
    :param outputs: list of output attribute full names.
    """
    if inputs:
        for attr_input in inputs:
            existing_inputs = cmds.listConnections(attribute, s=True, d=False, plugs=True)
            if existing_inputs:
                make_shared_connection(attr_input, attribute)
            else:
                try:
                    cmds.connectAttr(attr_input, attribute, f=True)
                except Exception:
                    pass

    if outputs:
        attr_type = cmds.getAttr(attribute, type=True)
        if attr_type in ['long', 'bool', 'double', 'enum', 'double3']:
            for attr_output in outputs:
                existing_inputs = cmds.listConnections(attr_output, s=True, d=False, plugs=True)
                if existing_inputs:
                    make_shared_connection(attribute, attr_output)
                else:
                    try:
                        cmds.connectAttr(attribute, attr_output, f=True)
                    except Exception:
                        pass


def make_shared_connection(attr_source, target_attr):
    """
    It connects an attribute to other connected attribute by pairblend node.
    This way the target attribute does'nt lose their existing connections.
    :param attr_source: Source attribute full name.
    :param target_attr: Target attribute full name.
    """
    existing_inputs = cmds.listConnections(target_attr, s=True, d=False, plugs=True)
    if not existing_inputs:
        return
    attr_previous_connected = existing_inputs[0]

    pb = cmds.createNode('pairBlend')
    cmds.setAttr('%s.w' % pb, 0.5)

    # Determine if compound
    attr_type = cmds.getAttr(attr_previous_connected, type=True)
    is_compound = attr_type in ['double3', 'float3']

    d_previous = {True: '%s.inTranslate1' % pb, False: '%s.inTranslateX1' % pb}
    d_source = {True: '%s.inTranslate2' % pb, False: '%s.inTranslateX2' % pb}
    d_out = {True: '%s.outTranslate' % pb, False: '%s.outTranslateX' % pb}

    try:
        cmds.connectAttr(attr_previous_connected, d_previous[is_compound], f=True)
        cmds.connectAttr(attr_source, d_source[is_compound], f=True)
        cmds.connectAttr(d_out[is_compound], target_attr, f=True)
    except Exception:
        pass


def get_selected_attributes():
    """
    Get the selected attributes in the ChannelBox.
    If there are not attributes selected, this method returns a empty list.
    :return: list with the selected attributes.
    """
    attrs = cmds.channelBox('mainChannelBox', q=True, sma=True)
    if not attrs:
        return []
    return attrs


def get_all_user_attributes(node):
    """
    It gets all user defined attributes of a node.
    :param node: String node name.
    :return: list with all user defined attributes.
    """
    all_attributes = list()
    ud_attrs = cmds.listAttr(node, ud=True) or []
    for attr in ud_attrs:
        # Only include top-level attributes (no parent)
        if not _get_parent_attr(node, attr):
            all_attributes.append(attr)
    return all_attributes


def get_attr_info(node, attr_name):
    """
    Get all data of a passed attribute.
    The data that it returns depends on the type of attribute.
    :param node: String node name.
    :param attr_name: String attribute name.
    :return: dictionary with the necessary data to recreate the attribute.
    """
    attr_full = '{}.{}'.format(node, attr_name)
    attribute_type = cmds.getAttr(attr_full, type=True)

    d_data = dict()
    d_data['longName'] = cmds.attributeQuery(attr_name, node=node, longName=True)
    d_data['niceName'] = cmds.attributeQuery(attr_name, node=node, niceName=True)
    d_data['shortName'] = cmds.attributeQuery(attr_name, node=node, shortName=True)
    d_data['hidden'] = not cmds.attributeQuery(attr_name, node=node, hidden=True) == False
    d_data['keyable'] = cmds.getAttr(attr_full, keyable=True)

    if attribute_type in ['string']:
        d_data['dataType'] = attribute_type
    else:
        d_data['attributeType'] = attribute_type

    if attribute_type in ['long', 'double', 'bool']:
        try:
            d_data['defaultValue'] = cmds.attributeQuery(attr_name, node=node, listDefault=True)[0]
        except Exception:
            pass
        try:
            max_val = cmds.attributeQuery(attr_name, node=node, maximum=True)
            if max_val:
                d_data['maxValue'] = max_val[0]
        except Exception:
            pass
        try:
            min_val = cmds.attributeQuery(attr_name, node=node, minimum=True)
            if min_val:
                d_data['minValue'] = min_val[0]
        except Exception:
            pass

    if attribute_type in ['enum']:
        enums = cmds.attributeQuery(attr_name, node=node, listEnum=True)
        if enums:
            d_data['enumName'] = enums[0]

    parent = _get_parent_attr(node, attr_name)
    if parent:
        d_data['parent'] = parent

    return d_data


def get_attr_connections(node, attr_name):
    """
    It returns the inputs and outputs connections of an attribute.
    :param node: String node name.
    :param attr_name: String attribute name.
    :return: dictionary with the inputs and outputs connections (as full plug strings).
    """
    attr_full = '{}.{}'.format(node, attr_name)
    inputs = cmds.listConnections(attr_full, s=True, d=False, plugs=True) or []
    outputs = cmds.listConnections(attr_full, s=False, d=True, plugs=True) or []
    return {'inputs': inputs, 'outputs': outputs}


def select_attributes(attributes, nodes):
    """
    Selects the passed attributes in the main Channel Box.
    :param attributes: List of the attributes to select.
    :param nodes: List of the objects with the attributes to select
    """
    to_select = ['{}.{}'.format(n, a) for a in attributes for n in nodes]
    cmds.select(nodes, r=True)
    str_command = "import maya.cmds as cmds\ncmds.channelBox('mainChannelBox', e=True, select={}, update=True)"
    cmds.evalDeferred(str_command.format(to_select))


def move_up_attribute(*args):
    """
    It moves a selected attributes in the channel box one position up.
    :param args: list of arguments.
    """
    selected_attributes = get_selected_attributes()

    if not cmds.ls(sl=True) or not selected_attributes:
        print('Nothing Selected')
        return

    selected_items = cmds.ls(sl=True)
    last_parent = None

    for item in selected_items:
        for attribute in selected_attributes:

            parent_attr = _get_parent_attr(item, attribute)
            if parent_attr:
                attribute = parent_attr
                if attribute == last_parent:
                    continue
                last_parent = attribute

            all_attributes = get_all_user_attributes(item)

            if attribute not in all_attributes:
                continue

            pos_attr = all_attributes.index(attribute)
            if pos_attr == 0:
                continue

            below_attr = all_attributes[pos_attr - 1:]
            below_attr.remove(attribute)

            result = copy_attr(item, item, attribute, move=True)
            if not result:
                return

            for attr in below_attr:
                result = copy_attr(item, item, attr, move=True)
                if not result:
                    return

    select_attributes(selected_attributes, selected_items)


def move_down_attribute(*args):
    """
    It moves a selected attributes in the channel box one position down.
    :param args: list of arguments.
    """
    selected_attributes = get_selected_attributes()

    if not cmds.ls(sl=True) or not selected_attributes:
        print('Nothing Selected')
        return

    selected_items = cmds.ls(sl=True)
    last_parent = None

    for item in selected_items:
        for attribute in reversed(selected_attributes):

            parent_attr = _get_parent_attr(item, attribute)
            if parent_attr:
                attribute = parent_attr
                if attribute == last_parent:
                    continue
                last_parent = attribute

            all_attributes = get_all_user_attributes(item)

            if attribute not in all_attributes:
                continue

            pos_attr = all_attributes.index(attribute)
            if pos_attr == len(all_attributes) - 1:
                continue

            below_attr = all_attributes[pos_attr + 2:]

            result = copy_attr(item, item, attribute, move=True)
            if not result:
                return
            for attr in below_attr:
                result = copy_attr(item, item, attr, move=True)
                if not result:
                    return

    select_attributes(selected_attributes, selected_items)


def copy_attribute(*args):
    """
    Saves the selected items and user defined attributes for copy to other item.
    :param args: list of arguments
    """
    save_selected_attributes('copy')


def cut_attribute(*args):
    """
    Saves the selected items and user defined attributes for move to other item.
    :param args: list of arguments
    """
    save_selected_attributes('cut')


def save_selected_attributes(mode):
    """
    Saves the selected items and user defined attributes for copy or move to other item.
    :param mode: string. 'copy' to copy the attributes. Or 'cut' to move the attributes
    """
    global __jlr_copy_data
    global __jlr_copy_mode

    if not cmds.ls(sl=True):
        cmds.warning("Nothing selected.")
        return

    source_item = cmds.ls(sl=True)[-1]
    all_selected_attr = get_selected_attributes()

    if not all_selected_attr:
        cmds.warning("No attribute is selected.")
        return

    all_ud_attributes = get_all_user_attributes(source_item)
    ud_selected_attr = [attr for attr in all_selected_attr if attr in all_ud_attributes]

    if not ud_selected_attr:
        cmds.warning("No user defined attribute is selected.")
        return

    __jlr_copy_data = {'source_item': source_item, 'attributes': ud_selected_attr}
    __jlr_copy_mode = mode


def paste_attribute(*args):
    """
    Copies or Moves an attribute from one object to another object.
    :param args: list of arguments
    """
    global __jlr_copy_data
    global __jlr_copy_mode

    if not cmds.ls(sl=True):
        cmds.warning("Nothing selected.")
        return

    target_item = cmds.ls(sl=True)[-1]
    source_item = __jlr_copy_data['source_item']
    move_attr = __jlr_copy_mode == 'cut'
    for attr in __jlr_copy_data['attributes']:
        copy_attr(source_item, target_item, attr, move=move_attr)

    cmds.select(target_item)


def add_divider_attribute(*args):
    """
    Adds a divider attribute in the ChannelBox of last selected item.
    :param args: list of arguments
    """
    item = cmds.ls(sl=True)[-1]
    name = 'divider'
    cont = 0
    fullname = name + str(cont).zfill(2)

    ud_attrs = cmds.listAttr(item, ud=True) or []
    while fullname in ud_attrs:
        cont += 1
        fullname = name + str(cont).zfill(2)

    d_data = dict()
    d_data['longName'] = str(fullname)
    d_data['attributeType'] = 'enum'
    d_data['niceName'] = str(' ')
    d_data['hidden'] = False
    d_data['keyable'] = True
    d_data['enumName'] = str('-' * 15)
    create_attr(item, d_data)


def unlock_trs_attributes(*args):
    """
    Unlocks the translate, rotation and scale attributes.
    :param args: list of arguments.
    """
    import itertools
    for item in cmds.ls(sl=True):
        for attr in itertools.product(['t', 'r', 's'], ['x', 'y', 'z']):
            attr_full = '{}.{}'.format(item, ''.join(attr))
            try:
                cmds.setAttr(attr_full, lock=False)
            except Exception:
                pass
