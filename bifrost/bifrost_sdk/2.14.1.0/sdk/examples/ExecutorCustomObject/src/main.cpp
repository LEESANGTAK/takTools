//-
// =============================================================================
// Copyright 2024 Autodesk, Inc. All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// =============================================================================
//+

#include "ExecutorCustomObject.h"
#include "ExecutorCustomObjectValueData.h"

#include <Amino/Core/Array.h>
#include <Amino/Core/String.h>

#include <BifrostGraph/Executor/GraphContainer.h>
#include <BifrostGraph/Executor/Job.h>
#include <BifrostGraph/Executor/Library.h>
#include <BifrostGraph/Executor/Utility.h>
#include <BifrostGraph/Executor/Workspace.h>

#include <iostream>
#include <map>
#include <string>
#include <vector>

namespace {
void printError(const std::string& msg) { std::cerr << "Error: " << msg << "\n"; }

std::ostream& operator<<(std::ostream& os, const Bifrost::Math::float3& vec) {
    os << "[ " << vec.x << ", " << vec.y << ", " << vec.z << " ]";
    return os;
}

std::ostream& operator<<(std::ostream& os, const Examples::SDK::BoundingBox& bb) {
    os << "min " << bb.min << " max " << bb.max;
    return os;
}

void printHelp() {
    std::cout
        << "executor_custom_object: Bifrost example to shows how to execute a graph with a custom "
           "type and use TypeTranslation to convert it to/from Amino.\n"
        << "\n"
        << "This example runs a Bifrost graph from the command line.\n"
        << "\n"
        << "Usage: executor_custom_object [options]\n"
        << "\n"
        << "options:\n"
        << "\n"
        << "  --graph-name <name>       Specify the fully qualified name, including namespace, of\n"
        << "                            the graph to run (e.g. User::Compounds::MyComp).\n"
        << "  --config-file <name>      Specify a Bifrost config JSON file to be loaded.\n"
        << "  --definition-file <name>  Specify a Bifrost definition JSON file to be loaded.\n"
        << "  --help                    Print this information and exit.\n";
}

struct Options {
    // List of config file to load.
    Amino::Array<Amino::String> configFiles;

    // List of definition file to load.
    Amino::Array<Amino::String> definitionFiles;

    // The name of the graph (compound) to execute.
    Amino::String graphToExecute;

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

    if (!arguments.count("--graph-name")) {
        throw std::invalid_argument("--graph-name is required.");
    }
    if (arguments.count("--graph-name") > 1) {
        throw std::invalid_argument("--graph-name can only be used once.");
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
        } else if (argName == "--graph-name") {
            if (argValues.size() != 1) {
                throw std::invalid_argument("Invalid usage --graph-name <name>");
            }
            options.graphToExecute = argValues[0].c_str();
        } else if (argName == "--definition-file") {
            if (argValues.size() != 1) {
                throw std::invalid_argument("Invalid usage --definition-file <path>");
            }
            options.definitionFiles.push_back(argValues[0].c_str());
        } else if (argName == "--help") {
            if (!argValues.empty()) {
                throw std::invalid_argument("Invalid usage --help");
            }
        } else {
            throw std::invalid_argument(argName + " is not a valid argument.");
        }
    }
}
} // namespace

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
        "ExecutorCustomObject");
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
        const auto& list = configEnv->values("bifrost_pack_config_files");
        for (auto const& file : list) {
            options.configFiles.push_back(file);
        }

        // Get the packs to disable from the env variable
        const auto& disabled_list = configEnv->values("bifrost_disable_packs");
        for (auto const& pack : disabled_list) {
            disablePacks.push_back(pack);
        }
    }

    if (!workspace->loadConfigFiles(options.configFiles, disablePacks)) {
        printError("Failed to load the config files.");
        return EXIT_FAILURE;
    }

    //
    // Load into the Library all definition files specified on the command line.
    //
    BifrostGraph::Executor::Library&    library = workspace->getLibrary();
    BifrostGraph::Executor::StringArray nameList;
    for (const auto& definitionFile : options.definitionFiles) {
        if (!library.loadDefinitionFile(definitionFile.c_str(), nameList)) {
            std::string msg = "Failed to load the definition file: ";
            msg += definitionFile.c_str();
            printError(msg);
            return EXIT_FAILURE;
        }
    }

    //
    // Create a Bifrost GraphContainer and set its graph (compound) to be compiled/executed.
    //
    BifrostGraph::Executor::GraphContainer& graphContainer = workspace->addGraphContainer();
    if (!graphContainer.isValid()) {
        printError("Failed to create the Bifrost GraphContainer.");
        return EXIT_FAILURE;
    }
    if (!graphContainer.setGraph(options.graphToExecute,
                                 BifrostGraph::Executor::SetGraphMode::kDefault)) {
        std::string msg = "Failed to set the graph: ";
        msg += options.graphToExecute.c_str();
        printError(msg);
        return EXIT_FAILURE;
    }

    //
    // Compile the graph (compound).
    //
    std::cout << "Compiling the graph '" << options.graphToExecute.c_str() << "'..." << std::endl;
    if (graphContainer.compile(BifrostGraph::Executor::GraphCompilationMode::kInit) !=
        BifrostGraph::Executor::GraphCompilationStatus::kSuccess) {
        printError("Failed to compile the graph.");
        return EXIT_FAILURE;
    }

    //
    // Set the Job's input values.
    //
    BifrostGraph::Executor::Job& job = graphContainer.getJob();
    if (!job.isValid()) {
        printError("Failed to get the Bifrost Job.");
        return EXIT_FAILURE;
    }

    // Define the values used as inputs
    const Examples::SDK::BoundingBox bb{Bifrost::Math::float3{-1, -1, -1},
                                        Bifrost::Math::float3{1, 1, 1}};
    const Bifrost::Math::float3      translation{4, 3, 7};

    std::cout << "Setting input port values:" << std::endl;
    std::cout << " inBB:        " << bb << std::endl;
    std::cout << " translation: " << translation << std::endl;

    for (const auto& input : job.getInputs()) {
        ExecutorCustomObjectValueData data;
        if (input.name == "inBB") {
            data.setBoundingBox(bb);
        } else if (input.name == "translation") {
            data.setFloat3(translation);
        } else {
            std::string msg = "Unsupported port '";
            msg += input.name.asChar();
            msg += "'.";
            printError(msg);
            return EXIT_FAILURE;
        }
        if (!job.setInputValue(input, &data)) {
            std::string msg = "Failed to set value for input port named '";
            msg += input.name.asChar();
            msg += "'.";
            printError(msg);
            return EXIT_FAILURE;
        }
    }

    //
    // Execute the Job.
    //
    std::cout << "Executing the graph..." << std::endl;
    BifrostGraph::Executor::JobExecutionStatus status =
        job.execute(BifrostGraph::Executor::JobExecutionMode::kDefault);
    if (status == BifrostGraph::Executor::JobExecutionStatus::kInvalid) {
        printError("The job is invalid.");
        return EXIT_FAILURE;
    } else if (status == BifrostGraph::Executor::JobExecutionStatus::kFailure) {
        printError("The job was completed with errors.");
        return EXIT_FAILURE;
    }

    //
    // Get the Job's output values.
    //
    std::cout << "Getting output port values:" << std::endl;
    for (const auto& output : job.getOutputs()) {
        ExecutorCustomObjectValueData data;
        if (!job.getOutputValue(output, &data)) {
            std::string msg = "Failed to get the value for graph's output port named '";
            msg += output.name.c_str();
            msg += "'.";
            printError(msg);
            return EXIT_FAILURE;
        }
        std::cout << "  Output value for port '" << output.name.c_str() << "' "
                  << data.getBoundingBox() << std::endl;
    }
    return EXIT_SUCCESS;
}
