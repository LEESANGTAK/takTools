//-
// =============================================================================
// Copyright 2024 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//+

#include <Amino/Core/Array.h>
#include <Amino/Core/Ptr.h>
#include <Amino/Core/String.h>
#include <Amino/Core/TypeId.h>

#include <BifrostGraph/Executor/GraphContainer.h>
#include <BifrostGraph/Executor/Job.h>
#include <BifrostGraph/Executor/Library.h>
#include <BifrostGraph/Executor/Utility.h>
#include <BifrostGraph/Executor/Watchpoint.h>
#include <BifrostGraph/Executor/WatchpointLayout.h>
#include <BifrostGraph/Executor/Workspace.h>

#include "PeriodicTableElement.h"

#include <iostream>
#include <map>
#include <string>
#include <vector>

namespace {
void printError(const std::string& msg) { std::cerr << "Error: " << msg << "\n"; }

void printFailure(int atLine, std::string const& msg) {
    std::cout << "Failure at line " << atLine << ": " << msg << "\n";
}

void checkValue(int atLine, std::string const& expected, std::string const& got) {
    if (expected != got) {
        std::string msg = std::string{"Expected \""} + expected + "\" got \"" + got;
        printFailure(atLine, msg);
    }
}

void printHelp() {
    std::cout
        << "executor_watchpoint: Bifrost example to shows how to define watchpoint for custom"
           "type.\n"
        << "\n"
        << "This example runs a Bifrost graph from the command line.\n"
        << "\n"
        << "Usage: executor_watchpoint [options]\n"
        << "\n"
        << "options:\n"
        << "\n"
        << "  --config-file <name>      Specify a Bifrost config JSON file to be loaded.\n"
        << "  --help                    Print this information and exit.\n";
}

struct Options {
    // List of config file to load.
    Amino::Array<Amino::String> configFiles;

    bool printHelp = false;
};

void parseArgument(std::vector<std::string> const& args, Options& options) {
    if (args.size() == 1) {
        throw std::invalid_argument("Missing arguments");
    }

    auto startWith = [](const std::string& str, const std::string& prefix) {
        if (str.size() > prefix.size()) return str.compare(0, prefix.length(), prefix) == 0;
        return false;
    };

    std::multimap<std::string, std::vector<std::string>> arguments;
    auto                                                 it(arguments.end());
    for (auto itString = args.begin() + 1; itString != args.end(); ++itString) {
        auto const& arg = *itString;
        if (startWith(arg, "--")) {
            it = arguments.insert(std::make_pair(arg, std::vector<std::string>{}));
        } else {
            if (it != arguments.end()) {
                it->second.push_back(arg);
            } else {
                throw std::invalid_argument(arg + " is not a valid argument.");
            }
        }
    }

    if (arguments.count("--help")) {
        options.printHelp = true;
        return;
    }

    // validate argument and fill options
    for (const auto& elem : arguments) {
        const auto& argName   = elem.first;
        const auto& argValues = elem.second;
        if (argName == "--config-file") {
            if (argValues.size() != 1) {
                throw std::invalid_argument("Invalid usage --config-file <path>");
            }
            options.configFiles.push_back(argValues[0].c_str());
        } else if (argName == "--help") {
            if (!argValues.empty()) {
                throw std::invalid_argument("Invalid usage --help");
            }
        } else {
            throw std::invalid_argument(argName + " is not a valid argument.");
        }
    }
}
}

int main(int argc, char* argv[]) {
    Options options;
    try {
        std::vector<std::string> args(argv, argv + argc);
        parseArgument(args, options);
    } catch (const std::exception& ex) {
        printError(ex.what());
        return EXIT_FAILURE;
    }

    if (options.printHelp) {
        printHelp();
        return EXIT_SUCCESS;
    }

    //
    // Create the workspace that is the core component of the Executor SDK.
    //
    auto workspace = BifrostGraph::Executor::makeOwner<BifrostGraph::Executor::Workspace>(
        "ExecutorWatchpoint");
    if (!workspace) {
        printError("Failed to create the Bifrost Workspace.");
        return EXIT_FAILURE;
    }

    //
    // Load config files from the command line and from the known environment variables.
    //
    Amino::Array<Amino::String> disablePacks;

    auto configEnv =
        BifrostGraph::Executor::makeOwner<BifrostGraph::Executor::Utility::ConfigEnv>();
    if (configEnv) {
        // Get the config file paths from the env variable
        auto configFiles = configEnv->values("bifrost_pack_config_files");
        for (auto const& configFile : configFiles) {
            options.configFiles.push_back(configFile);
        }
        // Get the packs to disable from the env variable
        disablePacks = configEnv->values("bifrost_disable_packs");
    }

    if (!workspace->loadConfigFiles(options.configFiles, disablePacks)) {
        printError("Failed to load the config files.");
        return EXIT_FAILURE;
    }

    auto const& factory = workspace->getWatchpointLayoutFactory();
    if (!factory.isValid()) {
        printError("Invalid watchpoint layout factory.");
        return EXIT_FAILURE;
    }


    auto getPeriodicElement = [](Amino::String const& name) {
        bool found = false;
        Amino::MutablePtr<Examples::SDK::PeriodicTableElement> element;
        Examples::SDK::get_periodic_table_element(name, found, element);
        return element.toImmutable();
    };

    auto getWatchpointValue = [&factory](BifrostGraph::Executor::Watchpoint const* watchpoint,
                              Amino::Any const& anyValue,
                              Amino::String const& name = Amino::String{}) {
        Amino::String value;
        BifrostGraph::Executor::WatchpointLayoutPath path{name};
        watchpoint->getValue(factory, anyValue, path, value);
        return std::string{value.c_str()};
    };

    auto getWatcherValue = [&factory](BifrostGraph::Executor::Watchpoint::Watcher const* watcher,
                                      Amino::String const& name = Amino::String{}) {
        Amino::String value;
        BifrostGraph::Executor::WatchpointLayoutPath path{name};
        watcher->getValue(factory, path, value);
        return std::string{value.c_str()};
    };

    {
        auto typeId = Amino::getTypeId<Amino::Ptr<Examples::SDK::PeriodicTableElement>>();
        auto watchpoint = workspace->getWatchpoint(typeId);
        if (!watchpoint) {
            printError("Failed to get watchpoint for type PeriodicTableElement.");
            return EXIT_FAILURE;
        }

        auto const element  = getPeriodicElement("manganese");
        auto const anyValue = Amino::Any{element};

        std::cout << "Watchpoint PeriodicTableElement ";
        std::cout << getWatchpointValue(watchpoint, anyValue)
                  << " -- [ name: " << getWatchpointValue(watchpoint, anyValue, "name")
                  << " -- symbol: " << getWatchpointValue(watchpoint, anyValue, "symbol")
                  << " -- number: " << getWatchpointValue(watchpoint, anyValue, "number")
                  << " -- mass: " << getWatchpointValue(watchpoint, anyValue, "mass")
                  << " ]\n";
        checkValue(__LINE__, "(Mn, 25)", getWatchpointValue(watchpoint, anyValue));
        checkValue(__LINE__, "Manganese", getWatchpointValue(watchpoint, anyValue, "name"));
        checkValue(__LINE__, "Mn", getWatchpointValue(watchpoint, anyValue, "symbol"));
        checkValue(__LINE__, "25", getWatchpointValue(watchpoint, anyValue, "number"));
        checkValue(__LINE__, "54.938046", getWatchpointValue(watchpoint, anyValue, "mass"));

        auto watcher = watchpoint->createWatcher(typeId);
        if (!watcher) {
            printError("Failed to create watcher for type PeriodicTableElement.");
            return EXIT_FAILURE;
        }
        auto callback = watchpoint->getCallBackFunction(typeId);
        if (!callback) {
            printError("Failed to get the watchpoint callback function for type PeriodicTableElement.");
            return EXIT_FAILURE;
        }

        // set the value on the watcher
        callback(watcher, 0 /*not used*/, &element);

        std::cout << "Watcher PeriodicTableElement ";
        std::cout << getWatcherValue(watcher)
                  << " -- [ name: " << getWatcherValue(watcher, "name")
                  << " -- symbol: " << getWatcherValue(watcher, "symbol")
                  << " -- number: " << getWatcherValue(watcher, "number")
                  << " -- mass: " << getWatcherValue(watcher, "mass")
                  << " ]\n";
        checkValue(__LINE__, "(Mn, 25)", getWatcherValue(watcher));
        checkValue(__LINE__, "Manganese", getWatcherValue(watcher, "name"));
        checkValue(__LINE__, "Mn", getWatcherValue(watcher, "symbol"));
        checkValue(__LINE__, "25", getWatcherValue(watcher, "number"));
        checkValue(__LINE__, "54.938046", getWatcherValue(watcher, "mass"));

        watcher->deleteThis();
    }
    {
        auto typeId = Amino::getTypeId<Amino::Ptr<Amino::Array<Amino::Ptr<Examples::SDK::PeriodicTableElement>>>>();
        auto watchpoint = workspace->getWatchpoint(typeId);
        if (!watchpoint) {
            printError("Failed to get watchpoint for type array<PeriodicTableElement>.");
            return EXIT_FAILURE;
        }
        auto const elements = [&getPeriodicElement]() {
            auto arrayPtr = Amino::newMutablePtr<Amino::Array<Amino::Ptr<Examples::SDK::PeriodicTableElement>>>(5llu);
            arrayPtr->at(0ull) = getPeriodicElement("radon");
            arrayPtr->at(1ull) = getPeriodicElement("nihonium");
            arrayPtr->at(2ull) = getPeriodicElement("arsenic");
            arrayPtr->at(3ull) = getPeriodicElement("uranium");
            arrayPtr->at(4ull) = getPeriodicElement("zirconium");
            return arrayPtr.toImmutable();
        }();
        auto const anyValue = Amino::Any{elements};

        std::cout << "Watchpoint array<PeriodicTableElement> (" << elements->size() << " elements)\n"
                  << " -- #2: " << getWatchpointValue(watchpoint, anyValue, "#2")
                  << " -- #2.name: " << getWatchpointValue(watchpoint, anyValue, "#2.name") << "\n"
                  << " -- #4: " << getWatchpointValue(watchpoint, anyValue, "#4")
                  << " -- #4.name: " << getWatchpointValue(watchpoint, anyValue, "#4.name") << "\n";
        checkValue(__LINE__, "(As, 33)", getWatchpointValue(watchpoint, anyValue, "#2"));
        checkValue(__LINE__, "Arsenic", getWatchpointValue(watchpoint, anyValue, "#2.name"));
        checkValue(__LINE__, "(Zr, 40)", getWatchpointValue(watchpoint, anyValue, "#4"));
        checkValue(__LINE__, "Zirconium", getWatchpointValue(watchpoint, anyValue, "#4.name"));

        auto watcher = watchpoint->createWatcher(typeId);
        if (!watcher) {
            printError("Failed to create watcher for type array<PeriodicTableElement>.");
            return EXIT_FAILURE;
        }
        auto callback = watchpoint->getCallBackFunction(typeId);
        if (!callback) {
            printError("Failed to get the watchpoint callback function for type array<PeriodicTableElement>.");
            return EXIT_FAILURE;
        }

        // set the value on the watcher
        callback(watcher, 0 /*not used*/, &elements);

        std::cout << "Watcher array<PeriodicTableElement>\n"
                  << " -- #2: " << getWatcherValue(watcher, "#2")
                  << " -- #2.name: " << getWatcherValue(watcher, "#2.name") << "\n"
                  << " -- #4: " << getWatcherValue(watcher, "#4")
                  << " -- #4.name: " << getWatcherValue(watcher, "#4.name") << "\n";
        checkValue(__LINE__, "(As, 33)", getWatcherValue(watcher, "#2"));
        checkValue(__LINE__, "Arsenic", getWatcherValue(watcher, "#2.name"));
        checkValue(__LINE__, "(Zr, 40)", getWatcherValue(watcher, "#4"));
        checkValue(__LINE__, "Zirconium", getWatcherValue(watcher, "#4.name"));

        auto layout = watcher->getLayout(const_cast<BifrostGraph::Executor::WatchpointLayoutFactory&>(factory));
        if (!layout || !layout.isA<BifrostGraph::Executor::WatchpointLayoutArray>()) {
            printFailure(__LINE__, "Expected a WatchpointLayoutArray");
        } else {
            auto layoutElt2 = layout.getAs<BifrostGraph::Executor::WatchpointLayoutArray>().layout(2);
            if (!layoutElt2 || !layoutElt2.isA<BifrostGraph::Executor::WatchpointLayoutComposite>()) {
                printFailure(__LINE__, "Expected a WatchpointLayoutComposite for element #2");
            } else if (layoutElt2.getAs<BifrostGraph::Executor::WatchpointLayoutComposite>().size() != 4) {
                printFailure(__LINE__, "Expected 4 nested layouts in composite layout of element #");
            } else {
                if (!layoutElt2.getAs<BifrostGraph::Executor::WatchpointLayoutComposite>().get("name")) {
                    printFailure(__LINE__, "Expected a \"name\" nested layout in composite layout");
                }
                if (!layoutElt2.getAs<BifrostGraph::Executor::WatchpointLayoutComposite>().get("symbol")) {
                    printFailure(__LINE__, "Expected a \"symbol\" nested layout in composite layout");
                }
                if (!layoutElt2.getAs<BifrostGraph::Executor::WatchpointLayoutComposite>().get("number")) {
                    printFailure(__LINE__, "Expected a \"number\" nested layout in composite layout");
                }
                if (!layoutElt2.getAs<BifrostGraph::Executor::WatchpointLayoutComposite>().get("mass")) {
                    printFailure(__LINE__, "Expected a \"mass\" nested layout in composite layout");
                }
            }
        }

        watcher->deleteThis();
    }
}
