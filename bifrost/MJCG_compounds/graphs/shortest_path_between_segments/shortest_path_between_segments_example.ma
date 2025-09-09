//Maya ASCII 2022 scene
//Name: shortest_path_between_segments_example.ma
//Last modified: Wed, Jun 16, 2021 11:59:49 PM
//Codeset: 932
requires maya "2022";
requires "mtoa" "4.2.2";
requires -nodeType "bifrostGraphShape" -dataType "bifData" "bifrostGraph" "2.3.0.0-dev-202106090408-fa69a6e";
requires "stereoCamera" "10.0";
currentUnit -l centimeter -a degree -t film;
fileInfo "application" "maya";
fileInfo "product" "Maya 2022";
fileInfo "version" "2022";
fileInfo "cutIdentifier" "202102181415-29bfc1879c";
fileInfo "osv" "Windows 10 Pro v2009 (Build: 19042)";
fileInfo "UUID" "C33F8EB3-41B7-300F-825D-5C8500C69A8A";
createNode transform -s -n "persp";
	rename -uid "D941B61E-49BE-681E-0F73-80A41FD6F1B0";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 15.933084454232922 9.109540942163715 10.203724114267736 ;
	setAttr ".r" -type "double3" -2541.3383527130113 -1742.2000000000912 0 ;
createNode camera -s -n "perspShape" -p "persp";
	rename -uid "822AA268-4140-1797-3C08-5AA073B9CEE0";
	setAttr -k off ".v" no;
	setAttr ".fl" 34.999999999999993;
	setAttr ".coi" 20.230273843352911;
	setAttr ".imn" -type "string" "persp";
	setAttr ".den" -type "string" "persp_depth";
	setAttr ".man" -type "string" "persp_mask";
	setAttr ".tp" -type "double3" -0.47141786319432999 1.7215189904242405 -5.2722565556014143 ;
	setAttr ".hc" -type "string" "viewSet -p %camera";
	setAttr ".ai_translator" -type "string" "perspective";
createNode transform -s -n "top";
	rename -uid "59F90FFD-4935-9BC4-991A-D08F78020FC3";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 0 1000.1 0 ;
	setAttr ".r" -type "double3" -90 0 0 ;
createNode camera -s -n "topShape" -p "top";
	rename -uid "6153C372-46AB-88B9-3E66-F58188097C62";
	setAttr -k off ".v" no;
	setAttr ".rnd" no;
	setAttr ".coi" 1000.1;
	setAttr ".ow" 30;
	setAttr ".imn" -type "string" "top";
	setAttr ".den" -type "string" "top_depth";
	setAttr ".man" -type "string" "top_mask";
	setAttr ".hc" -type "string" "viewSet -t %camera";
	setAttr ".o" yes;
	setAttr ".ai_translator" -type "string" "orthographic";
createNode transform -s -n "front";
	rename -uid "417613C3-4EBB-4596-C4E2-7AAF1E8DC295";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 0 0 1000.1 ;
createNode camera -s -n "frontShape" -p "front";
	rename -uid "762A2A7C-4203-6637-5F61-8CA2F743E5FE";
	setAttr -k off ".v" no;
	setAttr ".rnd" no;
	setAttr ".coi" 1000.1;
	setAttr ".ow" 30;
	setAttr ".imn" -type "string" "front";
	setAttr ".den" -type "string" "front_depth";
	setAttr ".man" -type "string" "front_mask";
	setAttr ".hc" -type "string" "viewSet -f %camera";
	setAttr ".o" yes;
	setAttr ".ai_translator" -type "string" "orthographic";
createNode transform -s -n "side";
	rename -uid "FB167BAB-4D07-F0E9-9D93-6A97942C2F55";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 1000.1 0 0 ;
	setAttr ".r" -type "double3" 0 90 0 ;
createNode camera -s -n "sideShape" -p "side";
	rename -uid "D6CB7385-460A-CC7B-F7FA-7D934054EC6E";
	setAttr -k off ".v" no;
	setAttr ".rnd" no;
	setAttr ".coi" 1000.1;
	setAttr ".ow" 30;
	setAttr ".imn" -type "string" "side";
	setAttr ".den" -type "string" "side_depth";
	setAttr ".man" -type "string" "side_mask";
	setAttr ".hc" -type "string" "viewSet -s %camera";
	setAttr ".o" yes;
	setAttr ".ai_translator" -type "string" "orthographic";
createNode transform -n "bifrostGraph1";
	rename -uid "21640FD7-4511-8F46-75B5-7BAE2A6768A9";
createNode bifrostGraphShape -n "bifrostGraphShape1" -p "bifrostGraph1";
	rename -uid "2C37A44E-45F3-C722-97ED-17BEABB7CE22";
	addAttr -r false -ci true -k true -sn "first_line_start" -ln "first_line_start" 
		-at "float3" -nc 3;
	addAttr -r false -ci true -k true -sn "first_line_startx" -ln "first_line_startx" 
		-at "float" -p "first_line_start";
	addAttr -r false -ci true -k true -sn "first_line_starty" -ln "first_line_starty" 
		-at "float" -p "first_line_start";
	addAttr -r false -ci true -k true -sn "first_line_startz" -ln "first_line_startz" 
		-at "float" -p "first_line_start";
	addAttr -r false -ci true -k true -sn "first_line_end" -ln "first_line_end" -at "float3" 
		-nc 3;
	addAttr -r false -ci true -k true -sn "first_line_endx" -ln "first_line_endx" -at "float" 
		-p "first_line_end";
	addAttr -r false -ci true -k true -sn "first_line_endy" -ln "first_line_endy" -at "float" 
		-p "first_line_end";
	addAttr -r false -ci true -k true -sn "first_line_endz" -ln "first_line_endz" -at "float" 
		-p "first_line_end";
	addAttr -r false -ci true -k true -sn "second_line_start" -ln "second_line_start" 
		-at "float3" -nc 3;
	addAttr -r false -ci true -k true -sn "second_line_startx" -ln "second_line_startx" 
		-at "float" -p "second_line_start";
	addAttr -r false -ci true -k true -sn "second_line_starty" -ln "second_line_starty" 
		-at "float" -p "second_line_start";
	addAttr -r false -ci true -k true -sn "second_line_startz" -ln "second_line_startz" 
		-at "float" -p "second_line_start";
	addAttr -r false -ci true -k true -sn "second_line_end" -ln "second_line_end" -at "float3" 
		-nc 3;
	addAttr -r false -ci true -k true -sn "second_line_endx" -ln "second_line_endx" 
		-at "float" -p "second_line_end";
	addAttr -r false -ci true -k true -sn "second_line_endy" -ln "second_line_endy" 
		-at "float" -p "second_line_end";
	addAttr -r false -ci true -k true -sn "second_line_endz" -ln "second_line_endz" 
		-at "float" -p "second_line_end";
	addAttr -w false -ci true -sn "Core__Graph__terminal__final" -ln "Core__Graph__terminal__final" -ct "terminal_node_output_attribute" 
 		-ct "terminal_node_output_attribute" -dt "bifData";
	addAttr -w false -ci true -sn "Core__Graph__terminal__proxy" -ln "Core__Graph__terminal__proxy" -ct "terminal_node_output_attribute" 
 		-ct "terminal_node_output_attribute" -dt "bifData";
	addAttr -w false -ci true -sn "Core__Graph__terminal__diagnostic" -ln "Core__Graph__terminal__diagnostic" -ct "terminal_node_output_attribute" 
 		-ct "terminal_node_output_attribute" -dt "bifData";
	setAttr -k off ".v";
	setAttr -s 2 ".iog";
	setAttr ".covm[0]"  0 1 1;
	setAttr ".cdvm[0]"  0 1 1;
	setAttr ".sc" -type "string" (
		"{\"header\": {\"metadata\": [{\"metaName\": \"adskFileFormatVersion\", \"metaValue\": \"100L\"}]}, \"namespaces\": [], \"types\": [], \"compounds\": [{\"name\": \"bifrostGraphShape1\", \"metadata\": [{\"metaName\": \"io_nodes\", \"metadata\": [{\"metaName\": \"io_inodes\", \"metadata\": [{\"metaName\": \"input\", \"metadata\": [{\"metaName\": \"DisplayMode\", \"metaType\": \"string\", \"metaValue\": \"2\"}, {\"metaName\": \"LayoutPos\", \"metaType\": \"string\", \"metaValue\": \"-67.0324 -859.225\"}, {\"metaName\": \"io_ports\", \"metadata\": [{\"metaName\": \"first_line_start\"}, {\"metaName\": \"first_line_end\"}, {\"metaName\": \"second_line_start\"}, {\"metaName\": \"second_line_end\"}]}]}]}, {\"metaName\": \"io_onodes\", \"metadata\": [{\"metaName\": \"output\", \"metadata\": [{\"metaName\": \"DisplayMode\", \"metaType\": \"string\", \"metaValue\": \"2\"}, {\"metaName\": \"io_ports\"},"
		+ " {\"metaName\": \"LayoutPos\", \"metaType\": \"string\", \"metaValue\": \"3093.27 -391.11\"}]}]}]}, {\"metaName\": \"backdrop\", \"metadata\": [{\"metaName\": \"type\", \"metaType\": \"string\", \"metaValue\": \"backdrop\"}, {\"metaName\": \"color\", \"metaType\": \"string\", \"metaValue\": \"#4a6d49\"}, {\"metaName\": \"text\", \"metaType\": \"string\", \"metaValue\": \"Construct a strands object to draw the two segments we start with, and a 3rd segment representing the shortest path between the two segments, then set render settings and color.\"}, {\"metaName\": \"coords\", \"metaType\": \"string\", \"metaValue\": \"1266.06 -892.904 1551.65 536.109\"}]}, {\"metaName\": \"backdrop1\", \"metadata\": [{\"metaName\": \"type\", \"metaType\": \"string\", \"metaValue\": \"backdrop\"}, {\"metaName\": \"color\", \"metaType\": \"string\", \"metaValue\": \"#6d4444\"}, {\"metaName\": \"text\", \"metaType\":"
		+ " \"string\", \"metaValue\": \"Construct a point object to draw the two points which are closest from each other's segments, then set render settings and color.\"}, {\"metaName\": \"coords\", \"metaType\": \"string\", \"metaValue\": \"1265.12 -341.751 1247.61 410.025\"}]}, {\"metaName\": \"backdrop2\", \"metadata\": [{\"metaName\": \"type\", \"metaType\": \"string\", \"metaValue\": \"backdrop\"}, {\"metaName\": \"color\", \"metaType\": \"string\", \"metaValue\": \"#44536d\"}, {\"metaName\": \"text\", \"metaType\": \"string\", \"metaValue\": \"We get the segment ratios defining where on each segments\\nis the closest location to the opposite segment.\"}, {\"metaName\": \"coords\", \"metaType\": \"string\", \"metaValue\": \"227.119 -409.413 537.956 423.887\"}]}, {\"metaName\": \"backdrop3\", \"metadata\": [{\"metaName\": \"type\", \"metaType\": \"string\", \"metaValue\": \"backdrop\"}, {\"metaName\":"
		+ " \"color\", \"metaType\": \"string\", \"metaValue\": \"#6d6947\"}, {\"metaName\": \"text\", \"metaType\": \"string\", \"metaValue\": \"We use the ratios to get the closest position along each segments.\\n\"}, {\"metaName\": \"coords\", \"metaType\": \"string\", \"metaValue\": \"853.458 -659.139 383.057 426.613\"}]}, {\"metaName\": \"internal\", \"metaValue\": \"true\"}, {\"metaName\": \"_recentNode_\", \"metaType\": \"string\", \"metaValue\": \"BifrostGraph,MJCG::Core::Math,closest_line_to_line_ratios\"}, {\"metaName\": \"_recentNode_\", \"metaType\": \"string\", \"metaValue\": \"BifrostGraph,Core::Math,get_from_interpolated_array\"}, {\"metaName\": \"_recentNode_\", \"metaType\": \"string\", \"metaValue\": \"BifrostGraph,Core::Logic,almost_equal\"}, {\"metaName\": \"_recentNode_\", \"metaType\": \"string\", \"metaValue\": \"BifrostGraph,Modeling::Strands,create_arrow_strands\"}, {\"metaName\":"
		+ " \"_recentNode_\", \"metaType\": \"string\", \"metaValue\": \"BifrostGraph,Modeling::Strands,create_strands_along_normals\"}, {\"metaName\": \"ViewportRect\", \"metaType\": \"string\", \"metaValue\": \"-88.8026 -1284.06 3148.02 1817\"}], \"ports\": [{\"portName\": \"first_line_start\", \"portDirection\": \"input\", \"portType\": \"Math::float3\"}, {\"portName\": \"first_line_end\", \"portDirection\": \"input\", \"portType\": \"Math::float3\"}, {\"portName\": \"second_line_start\", \"portDirection\": \"input\", \"portType\": \"Math::float3\"}, {\"portName\": \"second_line_end\", \"portDirection\": \"input\", \"portType\": \"Math::float3\"}], \"compounds\": [{\"name\": \"get_closest_points\", \"metadata\": [{\"metaName\": \"_recentNode_\", \"metaType\": \"string\", \"metaValue\": \"BifrostGraph,Core::Math,subtract\"}, {\"metaName\": \"_recentNode_\", \"metaType\": \"string\", \"metaValue\":"
		+ " \"BifrostGraph,MJCG::Core::Math,distance_between_vectors\"}, {\"metaName\": \"_recentNode_\", \"metaType\": \"string\", \"metaValue\": \"output\"}, {\"metaName\": \"_recentNode_\", \"metaType\": \"string\", \"metaValue\": \"input\"}, {\"metaName\": \"_recentNode_\", \"metaType\": \"string\", \"metaValue\": \"BifrostGraph,Core::Graph,terminal\"}, {\"metaName\": \"ViewportRect\", \"metaType\": \"string\", \"metaValue\": \"-1121 -673 2242 1346\"}, {\"metaName\": \"io_nodes\", \"metadata\": [{\"metaName\": \"io_inodes\", \"metadata\": [{\"metaName\": \"input\", \"metadata\": [{\"metaName\": \"DisplayMode\", \"metaType\": \"string\", \"metaValue\": \"2\"}, {\"metaName\": \"LayoutPos\", \"metaType\": \"string\", \"metaValue\": \"-824.742 -137.548\"}, {\"metaName\": \"io_ports\", \"metadata\": [{\"metaName\": \"first_line_start\"}, {\"metaName\": \"first_line_end\"}, {\"metaName\": \"second_line_start\"},"
		+ " {\"metaName\": \"second_line_end\"}, {\"metaName\": \"first_ratio\"}, {\"metaName\": \"second_ratio\"}]}]}]}, {\"metaName\": \"io_onodes\", \"metadata\": [{\"metaName\": \"output\", \"metadata\": [{\"metaName\": \"DisplayMode\", \"metaType\": \"string\", \"metaValue\": \"2\"}, {\"metaName\": \"LayoutPos\", \"metaType\": \"string\", \"metaValue\": \"423.87 -146.264\"}, {\"metaName\": \"io_ports\", \"metadata\": [{\"metaName\": \"first_line_position\"}, {\"metaName\": \"second_line_position\"}]}]}]}]}], \"ports\": [{\"portName\": \"first_line_start\", \"portDirection\": \"input\"}, {\"portName\": \"first_line_end\", \"portDirection\": \"input\"}, {\"portName\": \"second_line_start\", \"portDirection\": \"input\"}, {\"portName\": \"second_line_end\", \"portDirection\": \"input\"}, {\"portName\": \"first_ratio\", \"portDirection\": \"input\"}, {\"portName\": \"second_ratio\", \"portDirection\":"
		+ " \"input\"}, {\"portName\": \"first_line_position\", \"portDirection\": \"output\"}, {\"portName\": \"second_line_position\", \"portDirection\": \"output\"}], \"compoundNodes\": [{\"nodeName\": \"lerp\", \"nodeType\": \"Core::Math::lerp\", \"metadata\": [{\"metaName\": \"DisplayMode\", \"metaType\": \"string\", \"metaValue\": \"2\"}, {\"metaName\": \"LayoutPos\", \"metaType\": \"string\", \"metaValue\": \"-462.732 -196.637\"}]}, {\"nodeName\": \"lerp1\", \"nodeType\": \"Core::Math::lerp\", \"metadata\": [{\"metaName\": \"DisplayMode\", \"metaType\": \"string\", \"metaValue\": \"2\"}, {\"metaName\": \"LayoutPos\", \"metaType\": \"string\", \"metaValue\": \"-453.344 38.5378\"}]}, {\"nodeName\": \"subtract\", \"nodeType\": \"Core::Math::subtract\", \"multiInPortNames\": [\"interpolated1\", \"interpolated\"], \"metadata\": [{\"metaName\": \"DisplayMode\", \"metaType\": \"string\", \"metaValue\":"
		+ " \"2\"}, {\"metaName\": \"LayoutPos\", \"metaType\": \"string\", \"metaValue\": \"-176.943 -89.4961\"}]}, {\"nodeName\": \"vector_length\", \"nodeType\": \"Core::Math::length\", \"metadata\": [{\"metaName\": \"DisplayMode\", \"metaType\": \"string\", \"metaValue\": \"2\"}, {\"metaName\": \"LayoutPos\", \"metaType\": \"string\", \"metaValue\": \"110.257 21.9108\"}]}], \"connections\": [{\"source\": \"lerp.interpolated\", \"target\": \".first_line_position\"}, {\"source\": \"lerp.interpolated\", \"target\": \"subtract.first.interpolated\"}, {\"source\": \"lerp1.interpolated\", \"target\": \".second_line_position\"}, {\"source\": \"lerp1.interpolated\", \"target\": \"subtract.first.interpolated1\"}, {\"source\": \"subtract.output\", \"target\": \"vector_length.vector\"}, {\"source\": \".first_line_start\", \"target\": \"lerp.first\"}, {\"source\": \".first_line_end\", \"target\": \"lerp.second\"},"
		+ " {\"source\": \".second_line_start\", \"target\": \"lerp1.first\"}, {\"source\": \".second_line_end\", \"target\": \"lerp1.second\"}, {\"source\": \".first_ratio\", \"target\": \"lerp.fraction\"}, {\"source\": \".second_ratio\", \"target\": \"lerp1.fraction\"}], \"values\": [], \"reservedNodeNames\": [{\"name\": \"input\"}, {\"name\": \"output\"}]}], \"compoundNodes\": [{\"nodeName\": \"get_closest_points\", \"nodeType\": \"get_closest_points\", \"metadata\": [{\"metaName\": \"DisplayMode\", \"metaType\": \"string\", \"metaValue\": \"2\"}, {\"metaName\": \"LayoutPos\", \"metaType\": \"string\", \"metaValue\": \"934 -621\"}]}, {\"nodeName\": \"assign_diagnostic_material\", \"nodeType\": \"Diagnostic::Display::assign_diagnostic_material\", \"metadata\": [{\"metaName\": \"DisplayMode\", \"metaType\": \"string\", \"metaValue\": \"2\"}, {\"metaName\": \"LayoutPos\", \"metaType\": \"string\", \"metaValue\":"
		+ " \"2572.99 -873.649\"}]}, {\"nodeName\": \"build_array\", \"nodeType\": \"Core::Array::build_array\", \"multiInPortNames\": [\"output\", \"output1\", \"output2\", \"output3\", \"output4\", \"output5\"], \"metadata\": [{\"metaName\": \"DisplayMode\", \"metaType\": \"string\", \"metaValue\": \"2\"}, {\"metaName\": \"LayoutPos\", \"metaType\": \"string\", \"metaValue\": \"2305.83 -739.965\"}]}, {\"nodeName\": \"build_array1\", \"nodeType\": \"Core::Array::build_array\", \"multiInPortNames\": [\"output\", \"output2\"], \"metadata\": [{\"metaName\": \"DisplayMode\", \"metaType\": \"string\", \"metaValue\": \"2\"}, {\"metaName\": \"LayoutPos\", \"metaType\": \"string\", \"metaValue\": \"2014.41 -195.316\"}]}, {\"nodeName\": \"construct_points\", \"nodeType\": \"Geometry::Points::construct_points\", \"fanInPortNames\": {\"point_position\": [\"first_line_position\", \"second_line_position\"]}, \"metadata\":"
		+ " [{\"metaName\": \"DisplayMode\", \"metaType\": \"string\", \"metaValue\": \"2\"}, {\"metaName\": \"PortExpandedState\", \"metadata\": [{\"metaName\": \"point_position\", \"metaType\": \"string\", \"metaValue\": \"0\"}]}, {\"metaName\": \"LayoutPos\", \"metaType\": \"string\", \"metaValue\": \"1295.24 -266.842\"}]}, {\"nodeName\": \"construct_strands\", \"nodeType\": \"Geometry::Strands::construct_strands\", \"fanInPortNames\": {\"point_position\": [\"first_line_start\", \"first_line_end\", \"second_line_start\", \"second_line_end\", \"first_line_position\", \"second_line_position\"], \"strand_offset\": [\"output\", \"output1\", \"output2\", \"output3\"]}, \"metadata\": [{\"metaName\": \"DisplayMode\", \"metaType\": \"string\", \"metaValue\": \"2\"}, {\"metaName\": \"PortExpandedState\", \"metadata\": [{\"metaName\": \"point_position\", \"metaType\": \"string\", \"metaValue\": \"0\"}]}, {\"metaName\":"
		+ " \"LayoutPos\", \"metaType\": \"string\", \"metaValue\": \"1586.2 -835.28\"}]}, {\"nodeName\": \"set_point_shape\", \"nodeType\": \"Geometry::Properties::set_point_shape\", \"metadata\": [{\"metaName\": \"DisplayMode\", \"metaType\": \"string\", \"metaValue\": \"2\"}, {\"metaName\": \"LayoutPos\", \"metaType\": \"string\", \"metaValue\": \"1545.29 -290.843\"}]}, {\"nodeName\": \"set_strands_shape\", \"nodeType\": \"Geometry::Strands::set_strands_shape\", \"metadata\": [{\"metaName\": \"DisplayMode\", \"metaType\": \"string\", \"metaValue\": \"2\"}, {\"metaName\": \"LayoutPos\", \"metaType\": \"string\", \"metaValue\": \"1832.5 -853.614\"}]}, {\"nodeName\": \"terminal\", \"nodeType\": \"Core::Graph::terminal\", \"fanInPortNames\": {\"final\": [], \"proxy\": [\"geometry_with_material\", \"geometry_with_material1\"], \"diagnostic\": []}, \"deactivatedTerminals\": [\"Core::Graph::terminal::final\","
		+ " \"Core::Graph::terminal::diagnostic\"], \"metadata\": [{\"metaName\": \"DisplayMode\", \"metaType\": \"string\", \"metaValue\": \"2\"}, {\"metaName\": \"LayoutPos\", \"metaType\": \"string\", \"metaValue\": \"2865.51 -419.297\"}]}, {\"nodeName\": \"value\", \"valueType\": \"uint\", \"metadata\": [{\"metaName\": \"DisplayMode\", \"metaType\": \"string\", \"metaValue\": \"0\"}, {\"metaName\": \"valuenode_defaultvalue\", \"metaType\": \"string\", \"metaValue\": \"0\"}, {\"metaName\": \"LayoutPos\", \"metaType\": \"string\", \"metaValue\": \"1301.32 -857.298\"}]}, {\"nodeName\": \"value1\", \"valueType\": \"uint\", \"metadata\": [{\"metaName\": \"DisplayMode\", \"metaType\": \"string\", \"metaValue\": \"0\"}, {\"metaName\": \"valuenode_defaultvalue\", \"metaType\": \"string\", \"metaValue\": \"2\"}, {\"metaName\": \"LayoutPos\", \"metaType\": \"string\", \"metaValue\": \"1297.85 -728.526\"}]},"
		+ " {\"nodeName\": \"value2\", \"valueType\": \"uint\", \"metadata\": [{\"metaName\": \"DisplayMode\", \"metaType\": \"string\", \"metaValue\": \"0\"}, {\"metaName\": \"valuenode_defaultvalue\", \"metaType\": \"string\", \"metaValue\": \"4\"}, {\"metaName\": \"LayoutPos\", \"metaType\": \"string\", \"metaValue\": \"1297.95 -622.316\"}]}, {\"nodeName\": \"value3\", \"valueType\": \"uint\", \"metadata\": [{\"metaName\": \"DisplayMode\", \"metaType\": \"string\", \"metaValue\": \"0\"}, {\"metaName\": \"valuenode_defaultvalue\", \"metaType\": \"string\", \"metaValue\": \"6\"}, {\"metaName\": \"LayoutPos\", \"metaType\": \"string\", \"metaValue\": \"1298.06 -503.49\"}]}, {\"nodeName\": \"value5\", \"valueType\": \"Math::float3\", \"metadata\": [{\"metaName\": \"DisplayMode\", \"metaType\": \"string\", \"metaValue\": \"0\"}, {\"metaName\": \"valuenode_defaultvalue\", \"metaType\": \"string\", \"metaValue\":"
		+ " \"1\"}, {\"metaName\": \"valuenode_defaultvalue\", \"metaType\": \"string\", \"metaValue\": \"0\"}, {\"metaName\": \"valuenode_defaultvalue\", \"metaType\": \"string\", \"metaValue\": \"0\"}, {\"metaName\": \"LayoutPos\", \"metaType\": \"string\", \"metaValue\": \"2048.06 -765.368\"}]}, {\"nodeName\": \"value6\", \"valueType\": \"Math::float3\", \"metadata\": [{\"metaName\": \"DisplayMode\", \"metaType\": \"string\", \"metaValue\": \"0\"}, {\"metaName\": \"valuenode_defaultvalue\", \"metaType\": \"string\", \"metaValue\": \"0\"}, {\"metaName\": \"valuenode_defaultvalue\", \"metaType\": \"string\", \"metaValue\": \"1\"}, {\"metaName\": \"valuenode_defaultvalue\", \"metaType\": \"string\", \"metaValue\": \"0\"}, {\"metaName\": \"LayoutPos\", \"metaType\": \"string\", \"metaValue\": \"2049.06 -642.368\"}]}, {\"nodeName\": \"value7\", \"valueType\": \"Math::float3\", \"metadata\": [{\"metaName\":"
		+ " \"DisplayMode\", \"metaType\": \"string\", \"metaValue\": \"0\"}, {\"metaName\": \"valuenode_defaultvalue\", \"metaType\": \"string\", \"metaValue\": \"0\"}, {\"metaName\": \"valuenode_defaultvalue\", \"metaType\": \"string\", \"metaValue\": \"0\"}, {\"metaName\": \"valuenode_defaultvalue\", \"metaType\": \"string\", \"metaValue\": \"1\"}, {\"metaName\": \"LayoutPos\", \"metaType\": \"string\", \"metaValue\": \"2048.06 -524.368\"}]}, {\"nodeName\": \"value8\", \"valueType\": \"Math::float3\", \"metadata\": [{\"metaName\": \"DisplayMode\", \"metaType\": \"string\", \"metaValue\": \"0\"}, {\"metaName\": \"valuenode_defaultvalue\", \"metaType\": \"string\", \"metaValue\": \"1\"}, {\"metaName\": \"valuenode_defaultvalue\", \"metaType\": \"string\", \"metaValue\": \"0\"}, {\"metaName\": \"valuenode_defaultvalue\", \"metaType\": \"string\", \"metaValue\": \"0\"}, {\"metaName\": \"LayoutPos\","
		+ " \"metaType\": \"string\", \"metaValue\": \"1765.96 -191.211\"}]}, {\"nodeName\": \"value9\", \"valueType\": \"Math::float3\", \"metadata\": [{\"metaName\": \"DisplayMode\", \"metaType\": \"string\", \"metaValue\": \"0\"}, {\"metaName\": \"valuenode_defaultvalue\", \"metaType\": \"string\", \"metaValue\": \"0\"}, {\"metaName\": \"valuenode_defaultvalue\", \"metaType\": \"string\", \"metaValue\": \"1\"}, {\"metaName\": \"valuenode_defaultvalue\", \"metaType\": \"string\", \"metaValue\": \"0\"}, {\"metaName\": \"LayoutPos\", \"metaType\": \"string\", \"metaValue\": \"1762.96 -75.2112\"}]}, {\"nodeName\": \"assign_diagnostic_material2\", \"nodeType\": \"Diagnostic::Display::assign_diagnostic_material\", \"metadata\": [{\"metaName\": \"DisplayMode\", \"metaType\": \"string\", \"metaValue\": \"2\"}, {\"metaName\": \"LayoutPos\", \"metaType\": \"string\", \"metaValue\": \"2270.54 -313.597\"}]},"
		+ " {\"nodeName\": \"value10\", \"valueType\": \"MJCG::LineSegmentType\", \"metadata\": [{\"metaName\": \"DisplayMode\", \"metaType\": \"string\", \"metaValue\": \"2\"}, {\"metaName\": \"valuenode_defaultvalue\", \"metaType\": \"string\", \"metaValue\": \"1\"}, {\"metaName\": \"LayoutPos\", \"metaType\": \"string\", \"metaValue\": \"239.774 -179.575\"}]}, {\"nodeName\": \"closest_line_to_line_ratios\", \"nodeType\": \"MJCG::Core::Math::closest_line_to_line_ratios\", \"metadata\": [{\"metaName\": \"DisplayMode\", \"metaType\": \"string\", \"metaValue\": \"2\"}, {\"metaName\": \"LayoutPos\", \"metaType\": \"string\", \"metaValue\": \"497.329 -354.733\"}]}], \"connections\": [{\"source\": \".second_line_end\", \"target\": \"get_closest_points.second_line_end\"}, {\"source\": \".second_line_start\", \"target\": \"get_closest_points.second_line_start\"}, {\"source\": \".first_line_end\", \"target\":"
		+ " \"get_closest_points.first_line_end\"}, {\"source\": \".first_line_start\", \"target\": \"get_closest_points.first_line_start\"}, {\"source\": \"set_strands_shape.out_strands\", \"target\": \"assign_diagnostic_material.geometry\"}, {\"source\": \"build_array.array\", \"target\": \"assign_diagnostic_material.emission_color\"}, {\"source\": \"value5.output\", \"target\": \"build_array.first.output\"}, {\"source\": \"value5.output\", \"target\": \"build_array.first.output1\"}, {\"source\": \"value6.output\", \"target\": \"build_array.first.output2\"}, {\"source\": \"value6.output\", \"target\": \"build_array.first.output3\"}, {\"source\": \"value7.output\", \"target\": \"build_array.first.output4\"}, {\"source\": \"value7.output\", \"target\": \"build_array.first.output5\"}, {\"source\": \"value8.output\", \"target\": \"build_array1.first.output\"}, {\"source\": \"value9.output\", \"target\":"
		+ " \"build_array1.first.output2\"}, {\"source\": \"value.output\", \"target\": \"construct_strands.strand_offset.output\"}, {\"source\": \"value1.output\", \"target\": \"construct_strands.strand_offset.output1\"}, {\"source\": \"value2.output\", \"target\": \"construct_strands.strand_offset.output2\"}, {\"source\": \"value3.output\", \"target\": \"construct_strands.strand_offset.output3\"}, {\"source\": \"construct_points.points\", \"target\": \"set_point_shape.points\"}, {\"source\": \"construct_strands.strands\", \"target\": \"set_strands_shape.strands\"}, {\"source\": \"assign_diagnostic_material.geometry_with_material\", \"target\": \"terminal.proxy.geometry_with_material\"}, {\"source\": \"set_point_shape.out_points\", \"target\": \"assign_diagnostic_material2.geometry\"}, {\"source\": \"build_array1.array\", \"target\": \"assign_diagnostic_material2.emission_color\"}, {\"source\": \".first_line_start\","
		+ " \"target\": \"construct_strands.point_position.first_line_start\"}, {\"source\": \".first_line_end\", \"target\": \"construct_strands.point_position.first_line_end\"}, {\"source\": \".second_line_start\", \"target\": \"construct_strands.point_position.second_line_start\"}, {\"source\": \".second_line_end\", \"target\": \"construct_strands.point_position.second_line_end\"}, {\"source\": \"get_closest_points.first_line_position\", \"target\": \"construct_strands.point_position.first_line_position\"}, {\"source\": \"get_closest_points.first_line_position\", \"target\": \"construct_points.point_position.first_line_position\"}, {\"source\": \"get_closest_points.second_line_position\", \"target\": \"construct_strands.point_position.second_line_position\"}, {\"source\": \"get_closest_points.second_line_position\", \"target\": \"construct_points.point_position.second_line_position\"}, {\"source\":"
		+ " \"assign_diagnostic_material2.geometry_with_material\", \"target\": \"terminal.proxy.geometry_with_material1\"}, {\"source\": \".first_line_start\", \"target\": \"closest_line_to_line_ratios.first_line_start\"}, {\"source\": \".first_line_end\", \"target\": \"closest_line_to_line_ratios.first_line_end\"}, {\"source\": \".second_line_start\", \"target\": \"closest_line_to_line_ratios.second_line_start\"}, {\"source\": \".second_line_end\", \"target\": \"closest_line_to_line_ratios.second_line_end\"}, {\"source\": \"value10.output\", \"target\": \"closest_line_to_line_ratios.proximity_method\"}, {\"source\": \"closest_line_to_line_ratios.second_ratio\", \"target\": \"get_closest_points.second_ratio\"}, {\"source\": \"closest_line_to_line_ratios.first_ratio\", \"target\": \"get_closest_points.first_ratio\"}], \"values\": [{\"valueName\": \"assign_diagnostic_material.emission_color\", \"valueType\":"
		+ " \"string\", \"value\": \"color\"}, {\"valueName\": \"assign_diagnostic_material.specular\", \"valueType\": \"float\", \"value\": \"0f\"}, {\"valueName\": \"assign_diagnostic_material.emission\", \"valueType\": \"float\", \"value\": \"1f\"}, {\"valueName\": \"set_point_shape.points\", \"valueType\": \"Amino::Object\", \"value\": {}}, {\"valueName\": \"set_point_shape.shape\", \"valueType\": \"Geometry::PointShapes\", \"value\": \"Disk\"}, {\"valueName\": \"set_point_shape.screen_aligned\", \"valueType\": \"bool\", \"value\": \"true\"}, {\"valueName\": \"set_point_shape.numeric_property\", \"valueType\": \"string\", \"value\": \"point_position\"}, {\"valueName\": \"set_point_shape.default_size\", \"valueType\": \"float\", \"value\": \"0.200000003f\"}, {\"valueName\": \"set_strands_shape.strands\", \"valueType\": \"Amino::Object\", \"value\": {}}, {\"valueName\": \"set_strands_shape.shape\","
		+ " \"valueType\": \"Geometry::StrandShapes\", \"value\": \"Ribbon\"}, {\"valueName\": \"set_strands_shape.screen_aligned\", \"valueType\": \"bool\", \"value\": \"true\"}, {\"valueName\": \"set_strands_shape.default_size\", \"valueType\": \"float\", \"value\": \"0.0500000007f\"}, {\"valueName\": \"value.value\", \"valueType\": \"uint\", \"value\": \"0U\"}, {\"valueName\": \"value1.value\", \"valueType\": \"uint\", \"value\": \"2U\"}, {\"valueName\": \"value2.value\", \"valueType\": \"uint\", \"value\": \"4U\"}, {\"valueName\": \"value3.value\", \"valueType\": \"uint\", \"value\": \"6U\"}, {\"valueName\": \"value5.value\", \"valueType\": \"Math::float3\", \"value\": {\"x\": \"1f\", \"y\": \"0f\", \"z\": \"0f\"}}, {\"valueName\": \"value6.value\", \"valueType\": \"Math::float3\", \"value\": {\"x\": \"0f\", \"y\": \"1f\", \"z\": \"0f\"}}, {\"valueName\": \"value7.value\", \"valueType\": \"Math::float3\","
		+ " \"value\": {\"x\": \"0f\", \"y\": \"0f\", \"z\": \"1f\"}}, {\"valueName\": \"value8.value\", \"valueType\": \"Math::float3\", \"value\": {\"x\": \"1f\", \"y\": \"0f\", \"z\": \"0f\"}}, {\"valueName\": \"value9.value\", \"valueType\": \"Math::float3\", \"value\": {\"x\": \"0f\", \"y\": \"1f\", \"z\": \"0f\"}}, {\"valueName\": \"assign_diagnostic_material2.specular\", \"valueType\": \"float\", \"value\": \"0f\"}, {\"valueName\": \"assign_diagnostic_material2.emission\", \"valueType\": \"float\", \"value\": \"1f\"}, {\"valueName\": \"value10.value\", \"valueType\": \"MJCG::LineSegmentType\", \"value\": \"segment\"}], \"reservedNodeNames\": [{\"name\": \"input\"}, {\"name\": \"output\"}]}]}");
	setAttr ".dirtyFlag" yes;
	setAttr -k on ".first_line_start";
	setAttr -k on ".first_line_end";
	setAttr -k on ".second_line_start";
	setAttr -k on ".second_line_end";
createNode transform -n "locator1";
	rename -uid "2ECE59B0-4492-701E-6795-1B9F36A56F25";
	setAttr ".t" -type "double3" 1.4647110528498508 -0.16317920901836969 3.7286239273938722 ;
createNode locator -n "locatorShape1" -p "locator1";
	rename -uid "FD2046D6-4AA0-09E5-0D10-F3AD18BE63F4";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 13;
createNode transform -n "locator2";
	rename -uid "98B63471-4A06-2FA0-19F3-DBA0FC3493F2";
	setAttr ".t" -type "double3" -0.87801290885421857 5.1785450503322403 -4.9788329520060897 ;
createNode locator -n "locatorShape2" -p "locator2";
	rename -uid "F2B67523-48F1-8CF8-AC28-A695361A82FB";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 13;
createNode transform -n "locator3";
	rename -uid "ABD172B0-42BC-2FFA-A7F3-949270F855D4";
	setAttr ".t" -type "double3" -4.4855461064037589 4.1258831031460304 1.07741248440328 ;
createNode locator -n "locatorShape3" -p "locator3";
	rename -uid "B219A10C-43A5-F6B1-FE87-7CBF6B2D82E4";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 14;
createNode transform -n "locator4";
	rename -uid "3E23958E-433A-7917-8CF8-4D88F3DC467B";
	setAttr ".t" -type "double3" 7.2766955362998837 4.9061393629880978 1.0836141375877806 ;
createNode locator -n "locatorShape4" -p "locator4";
	rename -uid "6255B2AA-4129-5832-43C2-0C9EFB95C041";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 14;
createNode lightLinker -s -n "lightLinker1";
	rename -uid "64E0CD4E-47B0-F4DA-3ECE-4C94DF46F21E";
	setAttr -s 2 ".lnk";
	setAttr -s 2 ".slnk";
createNode shapeEditorManager -n "shapeEditorManager";
	rename -uid "8AC0F93F-44BD-E9ED-7576-2F8F64CC906E";
createNode poseInterpolatorManager -n "poseInterpolatorManager";
	rename -uid "A9BA3F52-4703-965C-6460-939B3CAB971C";
createNode displayLayerManager -n "layerManager";
	rename -uid "177A5B4C-4D74-E24E-952B-A4B2E874CA97";
createNode displayLayer -n "defaultLayer";
	rename -uid "2AC3E0AE-4D54-87FF-BC24-95B1C4AD1334";
createNode renderLayerManager -n "renderLayerManager";
	rename -uid "E75E64DA-483E-A88A-2E4D-E7A30070643E";
createNode renderLayer -n "defaultRenderLayer";
	rename -uid "DA47742E-4982-FEA3-6055-148BF4381250";
	setAttr ".g" yes;
createNode script -n "uiConfigurationScriptNode";
	rename -uid "2F3F9D16-4196-E016-8A70-9991C91CC7A2";
	setAttr ".b" -type "string" (
		"// Maya Mel UI Configuration File.\n//\n//  This script is machine generated.  Edit at your own risk.\n//\n//\n\nglobal string $gMainPane;\nif (`paneLayout -exists $gMainPane`) {\n\n\tglobal int $gUseScenePanelConfig;\n\tint    $useSceneConfig = $gUseScenePanelConfig;\n\tint    $nodeEditorPanelVisible = stringArrayContains(\"nodeEditorPanel1\", `getPanel -vis`);\n\tint    $nodeEditorWorkspaceControlOpen = (`workspaceControl -exists nodeEditorPanel1Window` && `workspaceControl -q -visible nodeEditorPanel1Window`);\n\tint    $menusOkayInPanels = `optionVar -q allowMenusInPanels`;\n\tint    $nVisPanes = `paneLayout -q -nvp $gMainPane`;\n\tint    $nPanes = 0;\n\tstring $editorName;\n\tstring $panelName;\n\tstring $itemFilterName;\n\tstring $panelConfig;\n\n\t//\n\t//  get current state of the UI\n\t//\n\tsceneUIReplacement -update $gMainPane;\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"modelPanel\" (localizedPanelLabel(\"Top View\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tmodelPanel -edit -l (localizedPanelLabel(\"Top View\")) -mbv $menusOkayInPanels  $panelName;\n"
		+ "\t\t$editorName = $panelName;\n        modelEditor -e \n            -docTag \"RADRENDER\" \n            -camera \"top\" \n            -useInteractiveMode 0\n            -displayLights \"default\" \n            -displayAppearance \"smoothShaded\" \n            -activeOnly 0\n            -ignorePanZoom 0\n            -wireframeOnShaded 0\n            -headsUpDisplay 1\n            -holdOuts 1\n            -selectionHiliteDisplay 1\n            -useDefaultMaterial 0\n            -bufferMode \"double\" \n            -twoSidedLighting 0\n            -backfaceCulling 0\n            -xray 0\n            -jointXray 0\n            -activeComponentsXray 0\n            -displayTextures 0\n            -smoothWireframe 0\n            -lineWidth 1\n            -textureAnisotropic 0\n            -textureHilight 1\n            -textureSampling 2\n            -textureDisplay \"modulate\" \n            -textureMaxSize 32768\n            -fogging 0\n            -fogSource \"fragment\" \n            -fogMode \"linear\" \n            -fogStart 0\n            -fogEnd 100\n            -fogDensity 0.1\n"
		+ "            -fogColor 0.5 0.5 0.5 1 \n            -depthOfFieldPreview 1\n            -maxConstantTransparency 1\n            -rendererName \"vp2Renderer\" \n            -objectFilterShowInHUD 1\n            -isFiltered 0\n            -colorResolution 256 256 \n            -bumpResolution 512 512 \n            -textureCompression 0\n            -transparencyAlgorithm \"frontAndBackCull\" \n            -transpInShadows 0\n            -cullingOverride \"none\" \n            -lowQualityLighting 0\n            -maximumNumHardwareLights 1\n            -occlusionCulling 0\n            -shadingModel 0\n            -useBaseRenderer 0\n            -useReducedRenderer 0\n            -smallObjectCulling 0\n            -smallObjectThreshold -1 \n            -interactiveDisableShadows 0\n            -interactiveBackFaceCull 0\n            -sortTransparent 1\n            -controllers 1\n            -nurbsCurves 1\n            -nurbsSurfaces 1\n            -polymeshes 1\n            -subdivSurfaces 1\n            -planes 1\n            -lights 1\n            -cameras 1\n"
		+ "            -controlVertices 1\n            -hulls 1\n            -grid 0\n            -imagePlane 1\n            -joints 1\n            -ikHandles 1\n            -deformers 1\n            -dynamics 1\n            -particleInstancers 1\n            -fluids 1\n            -hairSystems 1\n            -follicles 1\n            -nCloths 1\n            -nParticles 1\n            -nRigids 1\n            -dynamicConstraints 1\n            -locators 1\n            -manipulators 1\n            -pluginShapes 1\n            -dimensions 1\n            -handles 1\n            -pivots 1\n            -textures 1\n            -strokes 1\n            -motionTrails 1\n            -clipGhosts 1\n            -greasePencils 1\n            -shadows 0\n            -captureSequenceNumber -1\n            -width 1\n            -height 1\n            -sceneRenderFilter 0\n            $editorName;\n        modelEditor -e -viewSelected 0 $editorName;\n        modelEditor -e \n            -pluginObjects \"gpuCacheDisplayFilter\" 1 \n            $editorName;\n\t\tif (!$useSceneConfig) {\n"
		+ "\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"modelPanel\" (localizedPanelLabel(\"Side View\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tmodelPanel -edit -l (localizedPanelLabel(\"Side View\")) -mbv $menusOkayInPanels  $panelName;\n\t\t$editorName = $panelName;\n        modelEditor -e \n            -docTag \"RADRENDER\" \n            -camera \"side\" \n            -useInteractiveMode 0\n            -displayLights \"default\" \n            -displayAppearance \"smoothShaded\" \n            -activeOnly 0\n            -ignorePanZoom 0\n            -wireframeOnShaded 0\n            -headsUpDisplay 1\n            -holdOuts 1\n            -selectionHiliteDisplay 1\n            -useDefaultMaterial 0\n            -bufferMode \"double\" \n            -twoSidedLighting 0\n            -backfaceCulling 0\n            -xray 0\n            -jointXray 0\n            -activeComponentsXray 0\n            -displayTextures 0\n            -smoothWireframe 0\n            -lineWidth 1\n            -textureAnisotropic 0\n"
		+ "            -textureHilight 1\n            -textureSampling 2\n            -textureDisplay \"modulate\" \n            -textureMaxSize 32768\n            -fogging 0\n            -fogSource \"fragment\" \n            -fogMode \"linear\" \n            -fogStart 0\n            -fogEnd 100\n            -fogDensity 0.1\n            -fogColor 0.5 0.5 0.5 1 \n            -depthOfFieldPreview 1\n            -maxConstantTransparency 1\n            -rendererName \"vp2Renderer\" \n            -objectFilterShowInHUD 1\n            -isFiltered 0\n            -colorResolution 256 256 \n            -bumpResolution 512 512 \n            -textureCompression 0\n            -transparencyAlgorithm \"frontAndBackCull\" \n            -transpInShadows 0\n            -cullingOverride \"none\" \n            -lowQualityLighting 0\n            -maximumNumHardwareLights 1\n            -occlusionCulling 0\n            -shadingModel 0\n            -useBaseRenderer 0\n            -useReducedRenderer 0\n            -smallObjectCulling 0\n            -smallObjectThreshold -1 \n            -interactiveDisableShadows 0\n"
		+ "            -interactiveBackFaceCull 0\n            -sortTransparent 1\n            -controllers 1\n            -nurbsCurves 1\n            -nurbsSurfaces 1\n            -polymeshes 1\n            -subdivSurfaces 1\n            -planes 1\n            -lights 1\n            -cameras 1\n            -controlVertices 1\n            -hulls 1\n            -grid 1\n            -imagePlane 1\n            -joints 1\n            -ikHandles 1\n            -deformers 1\n            -dynamics 1\n            -particleInstancers 1\n            -fluids 1\n            -hairSystems 1\n            -follicles 1\n            -nCloths 1\n            -nParticles 1\n            -nRigids 1\n            -dynamicConstraints 1\n            -locators 1\n            -manipulators 1\n            -pluginShapes 1\n            -dimensions 1\n            -handles 1\n            -pivots 1\n            -textures 1\n            -strokes 1\n            -motionTrails 1\n            -clipGhosts 1\n            -greasePencils 1\n            -shadows 0\n            -captureSequenceNumber -1\n"
		+ "            -width 1\n            -height 1\n            -sceneRenderFilter 0\n            $editorName;\n        modelEditor -e -viewSelected 0 $editorName;\n        modelEditor -e \n            -pluginObjects \"gpuCacheDisplayFilter\" 1 \n            $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"modelPanel\" (localizedPanelLabel(\"Front View\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tmodelPanel -edit -l (localizedPanelLabel(\"Front View\")) -mbv $menusOkayInPanels  $panelName;\n\t\t$editorName = $panelName;\n        modelEditor -e \n            -docTag \"RADRENDER\" \n            -camera \"front\" \n            -useInteractiveMode 0\n            -displayLights \"default\" \n            -displayAppearance \"smoothShaded\" \n            -activeOnly 0\n            -ignorePanZoom 0\n            -wireframeOnShaded 0\n            -headsUpDisplay 1\n            -holdOuts 1\n            -selectionHiliteDisplay 1\n            -useDefaultMaterial 0\n"
		+ "            -bufferMode \"double\" \n            -twoSidedLighting 0\n            -backfaceCulling 0\n            -xray 0\n            -jointXray 0\n            -activeComponentsXray 0\n            -displayTextures 0\n            -smoothWireframe 0\n            -lineWidth 1\n            -textureAnisotropic 0\n            -textureHilight 1\n            -textureSampling 2\n            -textureDisplay \"modulate\" \n            -textureMaxSize 32768\n            -fogging 0\n            -fogSource \"fragment\" \n            -fogMode \"linear\" \n            -fogStart 0\n            -fogEnd 100\n            -fogDensity 0.1\n            -fogColor 0.5 0.5 0.5 1 \n            -depthOfFieldPreview 1\n            -maxConstantTransparency 1\n            -rendererName \"vp2Renderer\" \n            -objectFilterShowInHUD 1\n            -isFiltered 0\n            -colorResolution 256 256 \n            -bumpResolution 512 512 \n            -textureCompression 0\n            -transparencyAlgorithm \"frontAndBackCull\" \n            -transpInShadows 0\n            -cullingOverride \"none\" \n"
		+ "            -lowQualityLighting 0\n            -maximumNumHardwareLights 1\n            -occlusionCulling 0\n            -shadingModel 0\n            -useBaseRenderer 0\n            -useReducedRenderer 0\n            -smallObjectCulling 0\n            -smallObjectThreshold -1 \n            -interactiveDisableShadows 0\n            -interactiveBackFaceCull 0\n            -sortTransparent 1\n            -controllers 1\n            -nurbsCurves 1\n            -nurbsSurfaces 1\n            -polymeshes 1\n            -subdivSurfaces 1\n            -planes 1\n            -lights 1\n            -cameras 1\n            -controlVertices 1\n            -hulls 1\n            -grid 1\n            -imagePlane 1\n            -joints 1\n            -ikHandles 1\n            -deformers 1\n            -dynamics 1\n            -particleInstancers 1\n            -fluids 1\n            -hairSystems 1\n            -follicles 1\n            -nCloths 1\n            -nParticles 1\n            -nRigids 1\n            -dynamicConstraints 1\n            -locators 1\n            -manipulators 1\n"
		+ "            -pluginShapes 1\n            -dimensions 1\n            -handles 1\n            -pivots 1\n            -textures 1\n            -strokes 1\n            -motionTrails 1\n            -clipGhosts 1\n            -greasePencils 1\n            -shadows 0\n            -captureSequenceNumber -1\n            -width 1\n            -height 1\n            -sceneRenderFilter 0\n            $editorName;\n        modelEditor -e -viewSelected 0 $editorName;\n        modelEditor -e \n            -pluginObjects \"gpuCacheDisplayFilter\" 1 \n            $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"modelPanel\" (localizedPanelLabel(\"Persp View\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tmodelPanel -edit -l (localizedPanelLabel(\"Persp View\")) -mbv $menusOkayInPanels  $panelName;\n\t\t$editorName = $panelName;\n        modelEditor -e \n            -docTag \"RADRENDER\" \n            -camera \"persp\" \n            -useInteractiveMode 0\n            -displayLights \"default\" \n"
		+ "            -displayAppearance \"smoothShaded\" \n            -activeOnly 0\n            -ignorePanZoom 0\n            -wireframeOnShaded 0\n            -headsUpDisplay 1\n            -holdOuts 1\n            -selectionHiliteDisplay 1\n            -useDefaultMaterial 0\n            -bufferMode \"double\" \n            -twoSidedLighting 0\n            -backfaceCulling 0\n            -xray 0\n            -jointXray 0\n            -activeComponentsXray 0\n            -displayTextures 0\n            -smoothWireframe 0\n            -lineWidth 1\n            -textureAnisotropic 0\n            -textureHilight 1\n            -textureSampling 2\n            -textureDisplay \"modulate\" \n            -textureMaxSize 32768\n            -fogging 0\n            -fogSource \"fragment\" \n            -fogMode \"linear\" \n            -fogStart 0\n            -fogEnd 100\n            -fogDensity 0.1\n            -fogColor 0.5 0.5 0.5 1 \n            -depthOfFieldPreview 1\n            -maxConstantTransparency 1\n            -rendererName \"vp2Renderer\" \n            -objectFilterShowInHUD 1\n"
		+ "            -isFiltered 0\n            -colorResolution 256 256 \n            -bumpResolution 512 512 \n            -textureCompression 0\n            -transparencyAlgorithm \"frontAndBackCull\" \n            -transpInShadows 0\n            -cullingOverride \"none\" \n            -lowQualityLighting 0\n            -maximumNumHardwareLights 1\n            -occlusionCulling 0\n            -shadingModel 0\n            -useBaseRenderer 0\n            -useReducedRenderer 0\n            -smallObjectCulling 0\n            -smallObjectThreshold -1 \n            -interactiveDisableShadows 0\n            -interactiveBackFaceCull 0\n            -sortTransparent 1\n            -controllers 1\n            -nurbsCurves 1\n            -nurbsSurfaces 1\n            -polymeshes 1\n            -subdivSurfaces 1\n            -planes 1\n            -lights 1\n            -cameras 1\n            -controlVertices 1\n            -hulls 1\n            -grid 1\n            -imagePlane 1\n            -joints 1\n            -ikHandles 1\n            -deformers 1\n            -dynamics 1\n"
		+ "            -particleInstancers 1\n            -fluids 1\n            -hairSystems 1\n            -follicles 1\n            -nCloths 1\n            -nParticles 1\n            -nRigids 1\n            -dynamicConstraints 1\n            -locators 1\n            -manipulators 1\n            -pluginShapes 1\n            -dimensions 1\n            -handles 1\n            -pivots 1\n            -textures 1\n            -strokes 1\n            -motionTrails 1\n            -clipGhosts 1\n            -greasePencils 1\n            -shadows 0\n            -captureSequenceNumber -1\n            -width 2004\n            -height 542\n            -sceneRenderFilter 0\n            $editorName;\n        modelEditor -e -viewSelected 0 $editorName;\n        modelEditor -e \n            -pluginObjects \"gpuCacheDisplayFilter\" 1 \n            $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"outlinerPanel\" (localizedPanelLabel(\"Outliner\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n"
		+ "\t\toutlinerPanel -edit -l (localizedPanelLabel(\"Outliner\")) -mbv $menusOkayInPanels  $panelName;\n\t\t$editorName = $panelName;\n        outlinerEditor -e \n            -docTag \"isolOutln_fromSeln\" \n            -showShapes 0\n            -showAssignedMaterials 0\n            -showTimeEditor 1\n            -showReferenceNodes 0\n            -showReferenceMembers 0\n            -showAttributes 0\n            -showConnected 0\n            -showAnimCurvesOnly 0\n            -showMuteInfo 0\n            -organizeByLayer 1\n            -organizeByClip 1\n            -showAnimLayerWeight 1\n            -autoExpandLayers 1\n            -autoExpand 0\n            -showDagOnly 1\n            -showAssets 1\n            -showContainedOnly 1\n            -showPublishedAsConnected 0\n            -showParentContainers 0\n            -showContainerContents 1\n            -ignoreDagHierarchy 0\n            -expandConnections 0\n            -showUpstreamCurves 1\n            -showUnitlessCurves 1\n            -showCompounds 1\n            -showLeafs 1\n            -showNumericAttrsOnly 0\n"
		+ "            -highlightActive 1\n            -autoSelectNewObjects 0\n            -doNotSelectNewObjects 0\n            -dropIsParent 1\n            -transmitFilters 0\n            -setFilter \"defaultSetFilter\" \n            -showSetMembers 1\n            -allowMultiSelection 1\n            -alwaysToggleSelect 0\n            -directSelect 0\n            -isSet 0\n            -isSetMember 0\n            -displayMode \"DAG\" \n            -expandObjects 0\n            -setsIgnoreFilters 1\n            -containersIgnoreFilters 0\n            -editAttrName 0\n            -showAttrValues 0\n            -highlightSecondary 0\n            -showUVAttrsOnly 0\n            -showTextureNodesOnly 0\n            -attrAlphaOrder \"default\" \n            -animLayerFilterOptions \"allAffecting\" \n            -sortOrder \"none\" \n            -longNames 0\n            -niceNames 1\n            -showNamespace 1\n            -showPinIcons 0\n            -mapMotionTrails 0\n            -ignoreHiddenAttribute 0\n            -ignoreOutlinerColor 0\n            -renderFilterVisible 0\n"
		+ "            -renderFilterIndex 0\n            -selectionOrder \"chronological\" \n            -expandAttribute 0\n            $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"outlinerPanel\" (localizedPanelLabel(\"Outliner\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\toutlinerPanel -edit -l (localizedPanelLabel(\"Outliner\")) -mbv $menusOkayInPanels  $panelName;\n\t\t$editorName = $panelName;\n        outlinerEditor -e \n            -docTag \"isolOutln_fromSeln\" \n            -showShapes 0\n            -showAssignedMaterials 0\n            -showTimeEditor 1\n            -showReferenceNodes 0\n            -showReferenceMembers 0\n            -showAttributes 0\n            -showConnected 0\n            -showAnimCurvesOnly 0\n            -showMuteInfo 0\n            -organizeByLayer 1\n            -organizeByClip 1\n            -showAnimLayerWeight 1\n            -autoExpandLayers 1\n            -autoExpand 0\n            -showDagOnly 1\n"
		+ "            -showAssets 1\n            -showContainedOnly 1\n            -showPublishedAsConnected 0\n            -showParentContainers 0\n            -showContainerContents 1\n            -ignoreDagHierarchy 0\n            -expandConnections 0\n            -showUpstreamCurves 1\n            -showUnitlessCurves 1\n            -showCompounds 1\n            -showLeafs 1\n            -showNumericAttrsOnly 0\n            -highlightActive 1\n            -autoSelectNewObjects 0\n            -doNotSelectNewObjects 0\n            -dropIsParent 1\n            -transmitFilters 0\n            -setFilter \"defaultSetFilter\" \n            -showSetMembers 1\n            -allowMultiSelection 1\n            -alwaysToggleSelect 0\n            -directSelect 0\n            -displayMode \"DAG\" \n            -expandObjects 0\n            -setsIgnoreFilters 1\n            -containersIgnoreFilters 0\n            -editAttrName 0\n            -showAttrValues 0\n            -highlightSecondary 0\n            -showUVAttrsOnly 0\n            -showTextureNodesOnly 0\n            -attrAlphaOrder \"default\" \n"
		+ "            -animLayerFilterOptions \"allAffecting\" \n            -sortOrder \"none\" \n            -longNames 0\n            -niceNames 1\n            -showNamespace 1\n            -showPinIcons 0\n            -mapMotionTrails 0\n            -ignoreHiddenAttribute 0\n            -ignoreOutlinerColor 0\n            -renderFilterVisible 0\n            $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"graphEditor\" (localizedPanelLabel(\"Graph Editor\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Graph Editor\")) -mbv $menusOkayInPanels  $panelName;\n\n\t\t\t$editorName = ($panelName+\"OutlineEd\");\n            outlinerEditor -e \n                -showShapes 1\n                -showAssignedMaterials 0\n                -showTimeEditor 1\n                -showReferenceNodes 0\n                -showReferenceMembers 0\n                -showAttributes 1\n                -showConnected 1\n                -showAnimCurvesOnly 1\n"
		+ "                -showMuteInfo 0\n                -organizeByLayer 1\n                -organizeByClip 1\n                -showAnimLayerWeight 1\n                -autoExpandLayers 1\n                -autoExpand 1\n                -showDagOnly 0\n                -showAssets 1\n                -showContainedOnly 0\n                -showPublishedAsConnected 0\n                -showParentContainers 0\n                -showContainerContents 0\n                -ignoreDagHierarchy 0\n                -expandConnections 1\n                -showUpstreamCurves 1\n                -showUnitlessCurves 1\n                -showCompounds 0\n                -showLeafs 1\n                -showNumericAttrsOnly 1\n                -highlightActive 0\n                -autoSelectNewObjects 1\n                -doNotSelectNewObjects 0\n                -dropIsParent 1\n                -transmitFilters 1\n                -setFilter \"0\" \n                -showSetMembers 0\n                -allowMultiSelection 1\n                -alwaysToggleSelect 0\n                -directSelect 0\n"
		+ "                -displayMode \"DAG\" \n                -expandObjects 0\n                -setsIgnoreFilters 1\n                -containersIgnoreFilters 0\n                -editAttrName 0\n                -showAttrValues 0\n                -highlightSecondary 0\n                -showUVAttrsOnly 0\n                -showTextureNodesOnly 0\n                -attrAlphaOrder \"default\" \n                -animLayerFilterOptions \"allAffecting\" \n                -sortOrder \"none\" \n                -longNames 0\n                -niceNames 1\n                -showNamespace 1\n                -showPinIcons 1\n                -mapMotionTrails 1\n                -ignoreHiddenAttribute 0\n                -ignoreOutlinerColor 0\n                -renderFilterVisible 0\n                $editorName;\n\n\t\t\t$editorName = ($panelName+\"GraphEd\");\n            animCurveEditor -e \n                -displayValues 0\n                -snapTime \"integer\" \n                -snapValue \"none\" \n                -showPlayRangeShades \"on\" \n                -lockPlayRangeShades \"off\" \n"
		+ "                -smoothness \"fine\" \n                -resultSamples 1\n                -resultScreenSamples 0\n                -resultUpdate \"delayed\" \n                -showUpstreamCurves 1\n                -keyMinScale 1\n                -stackedCurvesMin -1\n                -stackedCurvesMax 1\n                -stackedCurvesSpace 0.2\n                -preSelectionHighlight 0\n                -constrainDrag 0\n                -valueLinesToggle 1\n                -outliner \"graphEditor1OutlineEd\" \n                -highlightAffectedCurves 0\n                $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"dopeSheetPanel\" (localizedPanelLabel(\"Dope Sheet\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Dope Sheet\")) -mbv $menusOkayInPanels  $panelName;\n\n\t\t\t$editorName = ($panelName+\"OutlineEd\");\n            outlinerEditor -e \n                -showShapes 1\n                -showAssignedMaterials 0\n"
		+ "                -showTimeEditor 1\n                -showReferenceNodes 0\n                -showReferenceMembers 0\n                -showAttributes 1\n                -showConnected 1\n                -showAnimCurvesOnly 1\n                -showMuteInfo 0\n                -organizeByLayer 1\n                -organizeByClip 1\n                -showAnimLayerWeight 1\n                -autoExpandLayers 1\n                -autoExpand 0\n                -showDagOnly 0\n                -showAssets 1\n                -showContainedOnly 0\n                -showPublishedAsConnected 0\n                -showParentContainers 0\n                -showContainerContents 0\n                -ignoreDagHierarchy 0\n                -expandConnections 1\n                -showUpstreamCurves 1\n                -showUnitlessCurves 0\n                -showCompounds 1\n                -showLeafs 1\n                -showNumericAttrsOnly 1\n                -highlightActive 0\n                -autoSelectNewObjects 0\n                -doNotSelectNewObjects 1\n                -dropIsParent 1\n"
		+ "                -transmitFilters 0\n                -setFilter \"0\" \n                -showSetMembers 0\n                -allowMultiSelection 1\n                -alwaysToggleSelect 0\n                -directSelect 0\n                -displayMode \"DAG\" \n                -expandObjects 0\n                -setsIgnoreFilters 1\n                -containersIgnoreFilters 0\n                -editAttrName 0\n                -showAttrValues 0\n                -highlightSecondary 0\n                -showUVAttrsOnly 0\n                -showTextureNodesOnly 0\n                -attrAlphaOrder \"default\" \n                -animLayerFilterOptions \"allAffecting\" \n                -sortOrder \"none\" \n                -longNames 0\n                -niceNames 1\n                -showNamespace 1\n                -showPinIcons 0\n                -mapMotionTrails 1\n                -ignoreHiddenAttribute 0\n                -ignoreOutlinerColor 0\n                -renderFilterVisible 0\n                $editorName;\n\n\t\t\t$editorName = ($panelName+\"DopeSheetEd\");\n            dopeSheetEditor -e \n"
		+ "                -displayValues 0\n                -snapTime \"integer\" \n                -snapValue \"none\" \n                -outliner \"dopeSheetPanel1OutlineEd\" \n                -showSummary 1\n                -showScene 0\n                -hierarchyBelow 0\n                -showTicks 1\n                -selectionWindow 0 0 0 0 \n                $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"timeEditorPanel\" (localizedPanelLabel(\"Time Editor\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Time Editor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"clipEditorPanel\" (localizedPanelLabel(\"Trax Editor\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Trax Editor\")) -mbv $menusOkayInPanels  $panelName;\n"
		+ "\n\t\t\t$editorName = clipEditorNameFromPanel($panelName);\n            clipEditor -e \n                -displayValues 0\n                -snapTime \"none\" \n                -snapValue \"none\" \n                -initialized 0\n                -manageSequencer 0 \n                $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"sequenceEditorPanel\" (localizedPanelLabel(\"Camera Sequencer\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Camera Sequencer\")) -mbv $menusOkayInPanels  $panelName;\n\n\t\t\t$editorName = sequenceEditorNameFromPanel($panelName);\n            clipEditor -e \n                -displayValues 0\n                -snapTime \"none\" \n                -snapValue \"none\" \n                -initialized 0\n                -manageSequencer 1 \n                $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"hyperGraphPanel\" (localizedPanelLabel(\"Hypergraph Hierarchy\")) `;\n"
		+ "\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Hypergraph Hierarchy\")) -mbv $menusOkayInPanels  $panelName;\n\n\t\t\t$editorName = ($panelName+\"HyperGraphEd\");\n            hyperGraph -e \n                -graphLayoutStyle \"hierarchicalLayout\" \n                -orientation \"horiz\" \n                -mergeConnections 0\n                -zoom 1\n                -animateTransition 0\n                -showRelationships 1\n                -showShapes 0\n                -showDeformers 0\n                -showExpressions 0\n                -showConstraints 0\n                -showConnectionFromSelected 0\n                -showConnectionToSelected 0\n                -showConstraintLabels 0\n                -showUnderworld 0\n                -showInvisible 0\n                -transitionFrames 1\n                -opaqueContainers 0\n                -freeform 0\n                -imagePosition 0 0 \n                -imageScale 1\n                -imageEnabled 0\n                -graphType \"DAG\" \n"
		+ "                -heatMapDisplay 0\n                -updateSelection 1\n                -updateNodeAdded 1\n                -useDrawOverrideColor 0\n                -limitGraphTraversal -1\n                -range 0 0 \n                -iconSize \"smallIcons\" \n                -showCachedConnections 0\n                $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"hyperShadePanel\" (localizedPanelLabel(\"Hypershade\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Hypershade\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"visorPanel\" (localizedPanelLabel(\"Visor\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Visor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n"
		+ "\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"nodeEditorPanel\" (localizedPanelLabel(\"Node Editor\")) `;\n\tif ($nodeEditorPanelVisible || $nodeEditorWorkspaceControlOpen) {\n\t\tif (\"\" == $panelName) {\n\t\t\tif ($useSceneConfig) {\n\t\t\t\t$panelName = `scriptedPanel -unParent  -type \"nodeEditorPanel\" -l (localizedPanelLabel(\"Node Editor\")) -mbv $menusOkayInPanels `;\n\n\t\t\t$editorName = ($panelName+\"NodeEditorEd\");\n            nodeEditor -e \n                -allAttributes 0\n                -allNodes 0\n                -autoSizeNodes 1\n                -consistentNameSize 1\n                -createNodeCommand \"nodeEdCreateNodeCommand\" \n                -connectNodeOnCreation 0\n                -connectOnDrop 0\n                -copyConnectionsOnPaste 0\n                -connectionStyle \"bezier\" \n                -connectionMinSegment 0.03\n                -connectionOffset 0.03\n                -connectionRoundness 0.8\n                -connectionTension -100\n                -defaultPinnedState 0\n"
		+ "                -additiveGraphingMode 1\n                -settingsChangedCallback \"nodeEdSyncControls\" \n                -traversalDepthLimit -1\n                -keyPressCommand \"nodeEdKeyPressCommand\" \n                -nodeTitleMode \"name\" \n                -gridSnap 0\n                -gridVisibility 1\n                -crosshairOnEdgeDragging 0\n                -popupMenuScript \"nodeEdBuildPanelMenus\" \n                -showNamespace 1\n                -showShapes 1\n                -showSGShapes 0\n                -showTransforms 1\n                -useAssets 1\n                -syncedSelection 1\n                -extendToShapes 1\n                -editorMode \"default\" \n                -hasWatchpoint 0\n                $editorName;\n\t\t\t}\n\t\t} else {\n\t\t\t$label = `panel -q -label $panelName`;\n\t\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Node Editor\")) -mbv $menusOkayInPanels  $panelName;\n\n\t\t\t$editorName = ($panelName+\"NodeEditorEd\");\n            nodeEditor -e \n                -allAttributes 0\n                -allNodes 0\n                -autoSizeNodes 1\n"
		+ "                -consistentNameSize 1\n                -createNodeCommand \"nodeEdCreateNodeCommand\" \n                -connectNodeOnCreation 0\n                -connectOnDrop 0\n                -copyConnectionsOnPaste 0\n                -connectionStyle \"bezier\" \n                -connectionMinSegment 0.03\n                -connectionOffset 0.03\n                -connectionRoundness 0.8\n                -connectionTension -100\n                -defaultPinnedState 0\n                -additiveGraphingMode 1\n                -settingsChangedCallback \"nodeEdSyncControls\" \n                -traversalDepthLimit -1\n                -keyPressCommand \"nodeEdKeyPressCommand\" \n                -nodeTitleMode \"name\" \n                -gridSnap 0\n                -gridVisibility 1\n                -crosshairOnEdgeDragging 0\n                -popupMenuScript \"nodeEdBuildPanelMenus\" \n                -showNamespace 1\n                -showShapes 1\n                -showSGShapes 0\n                -showTransforms 1\n                -useAssets 1\n                -syncedSelection 1\n"
		+ "                -extendToShapes 1\n                -editorMode \"default\" \n                -hasWatchpoint 0\n                $editorName;\n\t\t\tif (!$useSceneConfig) {\n\t\t\t\tpanel -e -l $label $panelName;\n\t\t\t}\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"createNodePanel\" (localizedPanelLabel(\"Create Node\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Create Node\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"polyTexturePlacementPanel\" (localizedPanelLabel(\"UV Editor\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"UV Editor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"renderWindowPanel\" (localizedPanelLabel(\"Render View\")) `;\n"
		+ "\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Render View\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"shapePanel\" (localizedPanelLabel(\"Shape Editor\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tshapePanel -edit -l (localizedPanelLabel(\"Shape Editor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"posePanel\" (localizedPanelLabel(\"Pose Editor\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tposePanel -edit -l (localizedPanelLabel(\"Pose Editor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"dynRelEdPanel\" (localizedPanelLabel(\"Dynamic Relationships\")) `;\n\tif (\"\" != $panelName) {\n"
		+ "\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Dynamic Relationships\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"relationshipPanel\" (localizedPanelLabel(\"Relationship Editor\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Relationship Editor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"referenceEditorPanel\" (localizedPanelLabel(\"Reference Editor\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Reference Editor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"componentEditorPanel\" (localizedPanelLabel(\"Component Editor\")) `;\n"
		+ "\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Component Editor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"dynPaintScriptedPanelType\" (localizedPanelLabel(\"Paint Effects\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Paint Effects\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"scriptEditorPanel\" (localizedPanelLabel(\"Script Editor\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Script Editor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"profilerPanel\" (localizedPanelLabel(\"Profiler Tool\")) `;\n"
		+ "\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Profiler Tool\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"contentBrowserPanel\" (localizedPanelLabel(\"Content Browser\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Content Browser\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"Stereo\" (localizedPanelLabel(\"Stereo\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Stereo\")) -mbv $menusOkayInPanels  $panelName;\n{ string $editorName = ($panelName+\"Editor\");\n            stereoCameraView -e \n                -editorChanged \"updateModelPanelBar\" \n                -camera \"persp\" \n                -useInteractiveMode 0\n"
		+ "                -displayLights \"default\" \n                -displayAppearance \"smoothShaded\" \n                -activeOnly 0\n                -ignorePanZoom 0\n                -wireframeOnShaded 0\n                -headsUpDisplay 1\n                -holdOuts 1\n                -selectionHiliteDisplay 1\n                -useDefaultMaterial 0\n                -bufferMode \"double\" \n                -twoSidedLighting 0\n                -backfaceCulling 0\n                -xray 0\n                -jointXray 0\n                -activeComponentsXray 0\n                -displayTextures 0\n                -smoothWireframe 0\n                -lineWidth 1\n                -textureAnisotropic 0\n                -textureHilight 1\n                -textureSampling 2\n                -textureDisplay \"modulate\" \n                -textureMaxSize 32768\n                -fogging 0\n                -fogSource \"fragment\" \n                -fogMode \"linear\" \n                -fogStart 0\n                -fogEnd 100\n                -fogDensity 0.1\n                -fogColor 0.5 0.5 0.5 1 \n"
		+ "                -depthOfFieldPreview 1\n                -maxConstantTransparency 1\n                -rendererOverrideName \"stereoOverrideVP2\" \n                -objectFilterShowInHUD 1\n                -isFiltered 0\n                -colorResolution 4 4 \n                -bumpResolution 4 4 \n                -textureCompression 0\n                -transparencyAlgorithm \"frontAndBackCull\" \n                -transpInShadows 0\n                -cullingOverride \"none\" \n                -lowQualityLighting 0\n                -maximumNumHardwareLights 0\n                -occlusionCulling 0\n                -shadingModel 0\n                -useBaseRenderer 0\n                -useReducedRenderer 0\n                -smallObjectCulling 0\n                -smallObjectThreshold -1 \n                -interactiveDisableShadows 0\n                -interactiveBackFaceCull 0\n                -sortTransparent 1\n                -controllers 1\n                -nurbsCurves 1\n                -nurbsSurfaces 1\n                -polymeshes 1\n                -subdivSurfaces 1\n"
		+ "                -planes 1\n                -lights 1\n                -cameras 1\n                -controlVertices 1\n                -hulls 1\n                -grid 1\n                -imagePlane 1\n                -joints 1\n                -ikHandles 1\n                -deformers 1\n                -dynamics 1\n                -particleInstancers 1\n                -fluids 1\n                -hairSystems 1\n                -follicles 1\n                -nCloths 1\n                -nParticles 1\n                -nRigids 1\n                -dynamicConstraints 1\n                -locators 1\n                -manipulators 1\n                -pluginShapes 1\n                -dimensions 1\n                -handles 1\n                -pivots 1\n                -textures 1\n                -strokes 1\n                -motionTrails 1\n                -clipGhosts 1\n                -greasePencils 1\n                -shadows 0\n                -captureSequenceNumber -1\n                -width 0\n                -height 0\n                -sceneRenderFilter 0\n"
		+ "                -displayMode \"centerEye\" \n                -viewColor 0 0 0 1 \n                -useCustomBackground 1\n                $editorName;\n            stereoCameraView -e -viewSelected 0 $editorName;\n            stereoCameraView -e \n                -pluginObjects \"gpuCacheDisplayFilter\" 1 \n                $editorName; };\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"outlinerPanel\" (localizedPanelLabel(\"ToggledOutliner\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\toutlinerPanel -edit -l (localizedPanelLabel(\"ToggledOutliner\")) -mbv $menusOkayInPanels  $panelName;\n\t\t$editorName = $panelName;\n        outlinerEditor -e \n            -showShapes 0\n            -showAssignedMaterials 0\n            -showTimeEditor 1\n            -showReferenceNodes 1\n            -showReferenceMembers 1\n            -showAttributes 0\n            -showConnected 0\n            -showAnimCurvesOnly 0\n            -showMuteInfo 0\n            -organizeByLayer 1\n"
		+ "            -organizeByClip 1\n            -showAnimLayerWeight 1\n            -autoExpandLayers 1\n            -autoExpand 0\n            -showDagOnly 1\n            -showAssets 1\n            -showContainedOnly 1\n            -showPublishedAsConnected 0\n            -showParentContainers 0\n            -showContainerContents 1\n            -ignoreDagHierarchy 0\n            -expandConnections 0\n            -showUpstreamCurves 1\n            -showUnitlessCurves 1\n            -showCompounds 1\n            -showLeafs 1\n            -showNumericAttrsOnly 0\n            -highlightActive 1\n            -autoSelectNewObjects 0\n            -doNotSelectNewObjects 0\n            -dropIsParent 1\n            -transmitFilters 0\n            -setFilter \"defaultSetFilter\" \n            -showSetMembers 1\n            -allowMultiSelection 1\n            -alwaysToggleSelect 0\n            -directSelect 0\n            -isSet 0\n            -isSetMember 0\n            -displayMode \"DAG\" \n            -expandObjects 0\n            -setsIgnoreFilters 1\n            -containersIgnoreFilters 0\n"
		+ "            -editAttrName 0\n            -showAttrValues 0\n            -highlightSecondary 0\n            -showUVAttrsOnly 0\n            -showTextureNodesOnly 0\n            -attrAlphaOrder \"default\" \n            -animLayerFilterOptions \"allAffecting\" \n            -sortOrder \"none\" \n            -longNames 0\n            -niceNames 1\n            -showNamespace 1\n            -showPinIcons 0\n            -mapMotionTrails 0\n            -ignoreHiddenAttribute 0\n            -ignoreOutlinerColor 0\n            -renderFilterVisible 0\n            -renderFilterIndex 0\n            -selectionOrder \"chronological\" \n            -expandAttribute 0\n            $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\tif ($useSceneConfig) {\n        string $configName = `getPanel -cwl (localizedPanelLabel(\"Current Layout\"))`;\n        if (\"\" != $configName) {\n\t\t\tpanelConfiguration -edit -label (localizedPanelLabel(\"Current Layout\")) \n\t\t\t\t-userCreated false\n\t\t\t\t-defaultImage \"vacantCell.xP:/\"\n\t\t\t\t-image \"\"\n\t\t\t\t-sc false\n"
		+ "\t\t\t\t-configString \"global string $gMainPane; paneLayout -e -cn \\\"single\\\" -ps 1 100 100 $gMainPane;\"\n\t\t\t\t-removeAllPanels\n\t\t\t\t-ap false\n\t\t\t\t\t(localizedPanelLabel(\"Persp View\")) \n\t\t\t\t\t\"modelPanel\"\n"
		+ "\t\t\t\t\t\"$panelName = `modelPanel -unParent -l (localizedPanelLabel(\\\"Persp View\\\")) -mbv $menusOkayInPanels `;\\n$editorName = $panelName;\\nmodelEditor -e \\n    -docTag \\\"RADRENDER\\\" \\n    -cam `findStartUpCamera persp` \\n    -useInteractiveMode 0\\n    -displayLights \\\"default\\\" \\n    -displayAppearance \\\"smoothShaded\\\" \\n    -activeOnly 0\\n    -ignorePanZoom 0\\n    -wireframeOnShaded 0\\n    -headsUpDisplay 1\\n    -holdOuts 1\\n    -selectionHiliteDisplay 1\\n    -useDefaultMaterial 0\\n    -bufferMode \\\"double\\\" \\n    -twoSidedLighting 0\\n    -backfaceCulling 0\\n    -xray 0\\n    -jointXray 0\\n    -activeComponentsXray 0\\n    -displayTextures 0\\n    -smoothWireframe 0\\n    -lineWidth 1\\n    -textureAnisotropic 0\\n    -textureHilight 1\\n    -textureSampling 2\\n    -textureDisplay \\\"modulate\\\" \\n    -textureMaxSize 32768\\n    -fogging 0\\n    -fogSource \\\"fragment\\\" \\n    -fogMode \\\"linear\\\" \\n    -fogStart 0\\n    -fogEnd 100\\n    -fogDensity 0.1\\n    -fogColor 0.5 0.5 0.5 1 \\n    -depthOfFieldPreview 1\\n    -maxConstantTransparency 1\\n    -rendererName \\\"vp2Renderer\\\" \\n    -objectFilterShowInHUD 1\\n    -isFiltered 0\\n    -colorResolution 256 256 \\n    -bumpResolution 512 512 \\n    -textureCompression 0\\n    -transparencyAlgorithm \\\"frontAndBackCull\\\" \\n    -transpInShadows 0\\n    -cullingOverride \\\"none\\\" \\n    -lowQualityLighting 0\\n    -maximumNumHardwareLights 1\\n    -occlusionCulling 0\\n    -shadingModel 0\\n    -useBaseRenderer 0\\n    -useReducedRenderer 0\\n    -smallObjectCulling 0\\n    -smallObjectThreshold -1 \\n    -interactiveDisableShadows 0\\n    -interactiveBackFaceCull 0\\n    -sortTransparent 1\\n    -controllers 1\\n    -nurbsCurves 1\\n    -nurbsSurfaces 1\\n    -polymeshes 1\\n    -subdivSurfaces 1\\n    -planes 1\\n    -lights 1\\n    -cameras 1\\n    -controlVertices 1\\n    -hulls 1\\n    -grid 1\\n    -imagePlane 1\\n    -joints 1\\n    -ikHandles 1\\n    -deformers 1\\n    -dynamics 1\\n    -particleInstancers 1\\n    -fluids 1\\n    -hairSystems 1\\n    -follicles 1\\n    -nCloths 1\\n    -nParticles 1\\n    -nRigids 1\\n    -dynamicConstraints 1\\n    -locators 1\\n    -manipulators 1\\n    -pluginShapes 1\\n    -dimensions 1\\n    -handles 1\\n    -pivots 1\\n    -textures 1\\n    -strokes 1\\n    -motionTrails 1\\n    -clipGhosts 1\\n    -greasePencils 1\\n    -shadows 0\\n    -captureSequenceNumber -1\\n    -width 2004\\n    -height 542\\n    -sceneRenderFilter 0\\n    $editorName;\\nmodelEditor -e -viewSelected 0 $editorName;\\nmodelEditor -e \\n    -pluginObjects \\\"gpuCacheDisplayFilter\\\" 1 \\n    $editorName\"\n"
		+ "\t\t\t\t\t\"modelPanel -edit -l (localizedPanelLabel(\\\"Persp View\\\")) -mbv $menusOkayInPanels  $panelName;\\n$editorName = $panelName;\\nmodelEditor -e \\n    -docTag \\\"RADRENDER\\\" \\n    -cam `findStartUpCamera persp` \\n    -useInteractiveMode 0\\n    -displayLights \\\"default\\\" \\n    -displayAppearance \\\"smoothShaded\\\" \\n    -activeOnly 0\\n    -ignorePanZoom 0\\n    -wireframeOnShaded 0\\n    -headsUpDisplay 1\\n    -holdOuts 1\\n    -selectionHiliteDisplay 1\\n    -useDefaultMaterial 0\\n    -bufferMode \\\"double\\\" \\n    -twoSidedLighting 0\\n    -backfaceCulling 0\\n    -xray 0\\n    -jointXray 0\\n    -activeComponentsXray 0\\n    -displayTextures 0\\n    -smoothWireframe 0\\n    -lineWidth 1\\n    -textureAnisotropic 0\\n    -textureHilight 1\\n    -textureSampling 2\\n    -textureDisplay \\\"modulate\\\" \\n    -textureMaxSize 32768\\n    -fogging 0\\n    -fogSource \\\"fragment\\\" \\n    -fogMode \\\"linear\\\" \\n    -fogStart 0\\n    -fogEnd 100\\n    -fogDensity 0.1\\n    -fogColor 0.5 0.5 0.5 1 \\n    -depthOfFieldPreview 1\\n    -maxConstantTransparency 1\\n    -rendererName \\\"vp2Renderer\\\" \\n    -objectFilterShowInHUD 1\\n    -isFiltered 0\\n    -colorResolution 256 256 \\n    -bumpResolution 512 512 \\n    -textureCompression 0\\n    -transparencyAlgorithm \\\"frontAndBackCull\\\" \\n    -transpInShadows 0\\n    -cullingOverride \\\"none\\\" \\n    -lowQualityLighting 0\\n    -maximumNumHardwareLights 1\\n    -occlusionCulling 0\\n    -shadingModel 0\\n    -useBaseRenderer 0\\n    -useReducedRenderer 0\\n    -smallObjectCulling 0\\n    -smallObjectThreshold -1 \\n    -interactiveDisableShadows 0\\n    -interactiveBackFaceCull 0\\n    -sortTransparent 1\\n    -controllers 1\\n    -nurbsCurves 1\\n    -nurbsSurfaces 1\\n    -polymeshes 1\\n    -subdivSurfaces 1\\n    -planes 1\\n    -lights 1\\n    -cameras 1\\n    -controlVertices 1\\n    -hulls 1\\n    -grid 1\\n    -imagePlane 1\\n    -joints 1\\n    -ikHandles 1\\n    -deformers 1\\n    -dynamics 1\\n    -particleInstancers 1\\n    -fluids 1\\n    -hairSystems 1\\n    -follicles 1\\n    -nCloths 1\\n    -nParticles 1\\n    -nRigids 1\\n    -dynamicConstraints 1\\n    -locators 1\\n    -manipulators 1\\n    -pluginShapes 1\\n    -dimensions 1\\n    -handles 1\\n    -pivots 1\\n    -textures 1\\n    -strokes 1\\n    -motionTrails 1\\n    -clipGhosts 1\\n    -greasePencils 1\\n    -shadows 0\\n    -captureSequenceNumber -1\\n    -width 2004\\n    -height 542\\n    -sceneRenderFilter 0\\n    $editorName;\\nmodelEditor -e -viewSelected 0 $editorName;\\nmodelEditor -e \\n    -pluginObjects \\\"gpuCacheDisplayFilter\\\" 1 \\n    $editorName\"\n"
		+ "\t\t\t\t$configName;\n\n            setNamedPanelLayout (localizedPanelLabel(\"Current Layout\"));\n        }\n\n        panelHistory -e -clear mainPanelHistory;\n        sceneUIReplacement -clear;\n\t}\n\n\ngrid -spacing 5 -size 12 -divisions 5 -displayAxes yes -displayGridLines yes -displayDivisionLines yes -displayPerspectiveLabels no -displayOrthographicLabels no -displayAxesBold yes -perspectiveLabelPosition axis -orthographicLabelPosition edge;\nviewManip -drawCompass 0 -compassAngle 0 -frontParameters \"\" -homeParameters \"\" -selectionLockParameters \"\";\n}\n");
	setAttr ".st" 3;
createNode script -n "sceneConfigurationScriptNode";
	rename -uid "FA3D20C8-4CD6-6231-8A71-AF872BE04CFC";
	setAttr ".b" -type "string" "playbackOptions -min 1 -max 120 -ast 1 -aet 200 ";
	setAttr ".st" 6;
createNode nodeGraphEditorInfo -n "MayaNodeEditorSavedTabsInfo";
	rename -uid "992B48A5-4D89-23B8-76CE-F79C19A5C482";
	setAttr ".tgi[0].tn" -type "string" "Untitled_1";
	setAttr ".tgi[0].vl" -type "double2" -255.92019575085084 -490.47617098641859 ;
	setAttr ".tgi[0].vh" -type "double2" 2117.8248836701673 -7.142856859025569 ;
	setAttr -s 5 ".tgi[0].ni";
	setAttr ".tgi[0].ni[0].x" 672.85711669921875;
	setAttr ".tgi[0].ni[0].y" -370;
	setAttr ".tgi[0].ni[0].nvs" 18304;
	setAttr ".tgi[0].ni[1].x" 672.85711669921875;
	setAttr ".tgi[0].ni[1].y" -167.14285278320312;
	setAttr ".tgi[0].ni[1].nvs" 18304;
	setAttr ".tgi[0].ni[2].x" 980;
	setAttr ".tgi[0].ni[2].y" -87.142860412597656;
	setAttr ".tgi[0].ni[2].nvs" 18305;
	setAttr ".tgi[0].ni[3].x" 672.85711669921875;
	setAttr ".tgi[0].ni[3].y" -268.57144165039062;
	setAttr ".tgi[0].ni[3].nvs" 18304;
	setAttr ".tgi[0].ni[4].x" 672.85711669921875;
	setAttr ".tgi[0].ni[4].y" -65.714286804199219;
	setAttr ".tgi[0].ni[4].nvs" 18304;
select -ne :time1;
	setAttr -av -k on ".cch";
	setAttr -av -cb on ".ihi";
	setAttr -av -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr -k on ".o" 4;
	setAttr -av -k on ".unw" 4;
	setAttr -av -k on ".etw";
	setAttr -av -k on ".tps";
	setAttr -av -k on ".tms";
select -ne :hardwareRenderingGlobals;
	setAttr -av -k on ".ihi";
	setAttr ".otfna" -type "stringArray" 22 "NURBS Curves" "NURBS Surfaces" "Polygons" "Subdiv Surface" "Particles" "Particle Instance" "Fluids" "Strokes" "Image Planes" "UI" "Lights" "Cameras" "Locators" "Joints" "IK Handles" "Deformers" "Motion Trails" "Components" "Hair Systems" "Follicles" "Misc. UI" "Ornaments"  ;
	setAttr ".otfva" -type "Int32Array" 22 0 1 1 1 1 1
		 1 1 1 0 0 0 0 0 0 0 0 0
		 0 0 0 0 ;
	setAttr -av ".ta";
	setAttr -av ".tq";
	setAttr -av ".etmr";
	setAttr -av ".tmr";
	setAttr -av ".aoon";
	setAttr -av ".aoam";
	setAttr -av ".aora";
	setAttr -av ".hfd";
	setAttr -av ".hfs";
	setAttr -av ".hfe";
	setAttr -av ".hfc";
	setAttr -av ".hfcr";
	setAttr -av ".hfcg";
	setAttr -av ".hfcb";
	setAttr -av ".hfa";
	setAttr -av ".mbe";
	setAttr -av -k on ".mbsof";
	setAttr -av ".msaa" yes;
	setAttr ".fprt" yes;
select -ne :renderPartition;
	setAttr -av -k on ".cch";
	setAttr -cb on ".ihi";
	setAttr -av -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr -s 2 ".st";
	setAttr -cb on ".an";
	setAttr -cb on ".pt";
select -ne :renderGlobalsList1;
	setAttr -k on ".cch";
	setAttr -cb on ".ihi";
	setAttr -k on ".nds";
	setAttr -cb on ".bnm";
select -ne :defaultShaderList1;
	setAttr -k on ".cch";
	setAttr -cb on ".ihi";
	setAttr -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr -s 5 ".s";
select -ne :postProcessList1;
	setAttr -k on ".cch";
	setAttr -cb on ".ihi";
	setAttr -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr -s 2 ".p";
select -ne :defaultRenderingList1;
	setAttr -k on ".ihi";
select -ne :initialShadingGroup;
	setAttr -av -k on ".cch";
	setAttr -k on ".fzn";
	setAttr -cb on ".ihi";
	setAttr -av -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr -k on ".bbx";
	setAttr -k on ".vwm";
	setAttr -k on ".tpv";
	setAttr -k on ".uit";
	setAttr -k on ".mwc";
	setAttr -cb on ".an";
	setAttr -cb on ".il";
	setAttr -cb on ".vo";
	setAttr -cb on ".eo";
	setAttr -cb on ".fo";
	setAttr -cb on ".epo";
	setAttr -k on ".ro" yes;
select -ne :initialParticleSE;
	setAttr -av -k on ".cch";
	setAttr -cb on ".ihi";
	setAttr -av -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr -k on ".mwc";
	setAttr -cb on ".an";
	setAttr -cb on ".il";
	setAttr -cb on ".vo";
	setAttr -cb on ".eo";
	setAttr -cb on ".fo";
	setAttr -cb on ".epo";
	setAttr -k on ".ro" yes;
select -ne :defaultRenderGlobals;
	addAttr -ci true -h true -sn "dss" -ln "defaultSurfaceShader" -dt "string";
	setAttr -av -k on ".cch";
	setAttr -cb on ".ihi";
	setAttr -av -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr -av -k on ".macc";
	setAttr -av -k on ".macd";
	setAttr -av -k on ".macq";
	setAttr -av -k on ".mcfr";
	setAttr -cb on ".ifg";
	setAttr -av -k on ".clip";
	setAttr -av -k on ".edm";
	setAttr -av -k on ".edl";
	setAttr -av -k on ".ren" -type "string" "arnold";
	setAttr -av -k on ".esr";
	setAttr -av -k on ".ors";
	setAttr -cb on ".sdf";
	setAttr -av -k on ".outf";
	setAttr -av -k on ".imfkey";
	setAttr -av -k on ".gama";
	setAttr -av -k on ".an";
	setAttr -cb on ".ar";
	setAttr -k on ".fs";
	setAttr -k on ".ef";
	setAttr -av -k on ".bfs";
	setAttr -cb on ".me";
	setAttr -cb on ".se";
	setAttr -av -k on ".be";
	setAttr -av -cb on ".ep";
	setAttr -av -k on ".fec";
	setAttr -av -k on ".ofc";
	setAttr -cb on ".ofe";
	setAttr -cb on ".efe";
	setAttr -cb on ".oft";
	setAttr -cb on ".umfn";
	setAttr -cb on ".ufe";
	setAttr -av -cb on ".pff";
	setAttr -av -k on ".peie";
	setAttr -av -cb on ".ifp";
	setAttr -k on ".rv";
	setAttr -av -k on ".comp";
	setAttr -av -k on ".cth";
	setAttr -av -k on ".soll";
	setAttr -cb on ".sosl";
	setAttr -av -k on ".rd";
	setAttr -av -k on ".lp";
	setAttr -av -k on ".sp";
	setAttr -av -k on ".shs";
	setAttr -av -k on ".lpr";
	setAttr -cb on ".gv";
	setAttr -cb on ".sv";
	setAttr -av -k on ".mm";
	setAttr -av -k on ".npu";
	setAttr -av -k on ".itf";
	setAttr -av -k on ".shp";
	setAttr -cb on ".isp";
	setAttr -av -k on ".uf";
	setAttr -av -k on ".oi";
	setAttr -av -k on ".rut";
	setAttr -av -k on ".mot";
	setAttr -av -cb on ".mb";
	setAttr -av -k on ".mbf";
	setAttr -av -k on ".mbso";
	setAttr -av -k on ".mbsc";
	setAttr -av -k on ".afp";
	setAttr -av -k on ".pfb";
	setAttr -k on ".pram";
	setAttr -k on ".poam";
	setAttr -k on ".prlm";
	setAttr -k on ".polm";
	setAttr -cb on ".prm";
	setAttr -cb on ".pom";
	setAttr -cb on ".pfrm";
	setAttr -cb on ".pfom";
	setAttr -av -k on ".bll";
	setAttr -av -k on ".bls";
	setAttr -av -k on ".smv";
	setAttr -av -k on ".ubc";
	setAttr -av -k on ".mbc";
	setAttr -cb on ".mbt";
	setAttr -av -k on ".udbx";
	setAttr -av -k on ".smc";
	setAttr -av -k on ".kmv";
	setAttr -cb on ".isl";
	setAttr -cb on ".ism";
	setAttr -cb on ".imb";
	setAttr -av -k on ".rlen";
	setAttr -av -k on ".frts";
	setAttr -av -k on ".tlwd";
	setAttr -av -k on ".tlht";
	setAttr -av -k on ".jfc";
	setAttr -cb on ".rsb";
	setAttr -av -k on ".ope";
	setAttr -av -k on ".oppf";
	setAttr -av -k on ".rcp";
	setAttr -av -k on ".icp";
	setAttr -av -k on ".ocp";
	setAttr -cb on ".hbl";
	setAttr ".dss" -type "string" "lambert1";
select -ne :defaultResolution;
	setAttr -av -k on ".cch";
	setAttr -av -k on ".ihi";
	setAttr -av -k on ".nds";
	setAttr -k on ".bnm";
	setAttr -av -k on ".w";
	setAttr -av -k on ".h";
	setAttr -av -k on ".pa" 1;
	setAttr -av -k on ".al";
	setAttr -av -k on ".dar";
	setAttr -av -k on ".ldar";
	setAttr -av -k on ".dpi";
	setAttr -av -k on ".off";
	setAttr -av -k on ".fld";
	setAttr -av -k on ".zsl";
	setAttr -av -k on ".isu";
	setAttr -av -k on ".pdu";
select -ne :defaultColorMgtGlobals;
	setAttr ".cfe" yes;
	setAttr ".cfp" -type "string" "<MAYA_RESOURCES>/OCIO-configs/Maya2022-default/config.ocio";
	setAttr ".wsn" -type "string" "ACEScg";
select -ne :hardwareRenderGlobals;
	setAttr -k on ".cch";
	setAttr -cb on ".ihi";
	setAttr -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr -av ".ctrs" 256;
	setAttr -av ".btrs" 512;
	setAttr -av -k off -cb on ".fbfm";
	setAttr -av -k off -cb on ".ehql";
	setAttr -av -k off -cb on ".eams";
	setAttr -av -k off -cb on ".eeaa";
	setAttr -av -k off -cb on ".engm";
	setAttr -av -k off -cb on ".mes";
	setAttr -av -k off -cb on ".emb";
	setAttr -av -k off -cb on ".mbbf";
	setAttr -av -k off -cb on ".mbs";
	setAttr -av -k off -cb on ".trm";
	setAttr -av -k off -cb on ".tshc";
	setAttr -av -k off -cb on ".enpt";
	setAttr -av -k off -cb on ".clmt";
	setAttr -av -k off -cb on ".tcov";
	setAttr -av -k off -cb on ".lith";
	setAttr -av -k off -cb on ".sobc";
	setAttr -av -k off -cb on ".cuth";
	setAttr -av -k off -cb on ".hgcd";
	setAttr -av -k off -cb on ".hgci";
	setAttr -av -k off -cb on ".mgcs";
	setAttr -av -k off -cb on ".twa";
	setAttr -av -k off -cb on ".twz";
	setAttr -cb on ".hwcc";
	setAttr -cb on ".hwdp";
	setAttr -cb on ".hwql";
	setAttr -k on ".hwfr";
	setAttr -k on ".soll";
	setAttr -k on ".sosl";
	setAttr -k on ".bswa";
	setAttr -k on ".shml";
	setAttr -k on ".hwel";
connectAttr "locator1.t" "bifrostGraphShape1.first_line_start";
connectAttr "locator4.t" "bifrostGraphShape1.second_line_end";
connectAttr "locator3.t" "bifrostGraphShape1.second_line_start";
connectAttr "locator2.t" "bifrostGraphShape1.first_line_end";
relationship "link" ":lightLinker1" ":initialShadingGroup.message" ":defaultLightSet.message";
relationship "link" ":lightLinker1" ":initialParticleSE.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" ":initialShadingGroup.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" ":initialParticleSE.message" ":defaultLightSet.message";
connectAttr "layerManager.dli[0]" "defaultLayer.id";
connectAttr "renderLayerManager.rlmi[0]" "defaultRenderLayer.rlid";
connectAttr "locator1.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[0].dn";
connectAttr "locator3.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[1].dn";
connectAttr "bifrostGraphShape1.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[2].dn"
		;
connectAttr "locator2.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[3].dn";
connectAttr "locator4.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[4].dn";
connectAttr "defaultRenderLayer.msg" ":defaultRenderingList1.r" -na;
connectAttr "bifrostGraphShape1.iog" ":initialShadingGroup.dsm" -na;
// End of shortest_path_between_segments_example.ma
