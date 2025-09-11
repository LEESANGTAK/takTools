//-
// ================================================================================================
// Copyright 2024 Autodesk, Inc.  All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license agreement provided
// at the time of installation or download, or which otherwise accompanies this software in
// either electronic or hard copy form.
// ================================================================================================
//+

/// \file Job.h
/// \brief BifrostGraph Executor Job.
/// \note The contents of this file belong to a feature that is still under development,
/// and they may change in subsequent versions.

#ifndef BIFROSTGRAPH_EXECUTOR_JOB_H
#define BIFROSTGRAPH_EXECUTOR_JOB_H

#include <BifrostGraph/Executor/Factory.h>
#include <BifrostGraph/Executor/TypeTranslation.h>

#include <BifrostGraph/Executor/internal/ExecutorExport.h>
#include <BifrostGraph/Executor/internal/PropagateConstPtr.h>

#include <Amino/Core/Any.h>
#include <Amino/Core/String.h>

//-------------------------------------------------------------------------------------------------
// Forward declarations
//-------------------------------------------------------------------------------------------------

namespace BifrostGraph {
namespace Executor {

class GraphContainer;
class Workspace;

namespace Private {
class IJobOwner;
class IRestrictedJobServices;
class JobImpl;
} // namespace Private

/// \ingroup BifrostGraphExecutor

//-------------------------------------------------------------------------------------------------
// CLASS Job
//-------------------------------------------------------------------------------------------------

/// \brief The Job class that executes a graph with inputs/outputs coming/going from/to host.
///
class BIFROSTGRAPH_EXECUTOR_SHARED_DECL Job final {
public:
    /// \brief A Job input descriptor.
    struct BIFROSTGRAPH_EXECUTOR_SHARED_DECL Input final {
        Amino::String name;         ///< The input's name.
        Amino::String typeName;     ///< The fully qualified name of the input's data type.
        Amino::Any    defaultValue; ///< The input's default value (coming from the graph).
        bool          isJobPort;    ///< Whether or not the input is a Job port.
    };
    /// \brief A collection of Job inputs.
    using Inputs = Amino::Array<Input>;

    /// \brief A Job output descriptor.
    struct BIFROSTGRAPH_EXECUTOR_SHARED_DECL Output final {
        Amino::String name;       ///< The output's name.
        Amino::String typeName;   ///< The fully qualified name of the output's data type.
        bool          isTerminal; ///< Whether or not the output is a Terminal.
        bool          isEnabled;  ///< Whether or not this output is enabled.
    };
    /// \brief A collection of Job outputs.
    using Outputs = Amino::Array<Output>;

private:
    //---------------------------------------------------------------------------------------------
    // Initialization
    //---------------------------------------------------------------------------------------------

    /// \brief Construct a Job. The new Job is owned and managed by the \ref GraphContainer.
    ///
    /// If an error occurs during the construction of this Job then
    /// \ref BifrostGraph::Executor::Job::isValid will return false and all future
    /// operations on this Job will fail.
    ///
    /// \param [in] owner The Job's owner. Only the GraphContainer can create an
    ///                   IJobOwner object required by this constructor, hence only
    ///                   the GraphContainer can initiate the construction of a Job (see
    ///                   GraphContainer's getJob method).
    explicit Job(Private::IJobOwner& owner) noexcept;

    /// \brief Constructor that leaves the Job in an uninitialized state.
    ///
    /// After this constructor returns, the method \ref BifrostGraph::Executor::Job::isValid
    /// will return false and all future operations on the Job will fail.
    ///
    /// \param [in] uninitialized  an Uninitialized enum value.
    explicit Job(Uninitialized uninitialized) noexcept;

    /// \brief Allow the makeOwner<> factory functions to access the constructors of this class.
    EXECUTOR_DECLARE_MAKE_OWNER_FRIENDSHIP();

public:
    /// \brief Destructor.
    ///
    /// The destructor should not be called directly since a Job is managed by the GraphContainer.
    ///
    ~Job() noexcept;

    /// \brief Check if this Job has been successfully initialized.
    ///
    /// If an error occurs during the construction of a Job, isValid() will
    /// return false and all future operations on the Job will fail.
    ///
    /// \return true if this Job has been successfully initialized and is ready to
    /// be used; false otherwise.
    bool isValid() const noexcept;

    /// \brief Get a statically allocated Job that is uninitialized, invalid and not
    /// owned by any GraphContainer.
    /// Any operation on this instance will always fail and \ref Job::isValid will return false.
    static Job& getInvalid() noexcept;

    /// \brief Access the \ref GraphContainer which owns this Job.
    /// \return A reference to the \ref GraphContainer which owns this Job, if this instance
    /// is valid (see \ref BifrostGraph::Executor::Job::isValid); an invalid \ref GraphContainer
    /// otherwise.
    /// \{
    const GraphContainer& getGraphContainer() const noexcept;
    GraphContainer&       getGraphContainer() noexcept;
    /// \}

    /// \brief Access this Job's Workspace ancestor, i.e. the one that owns the GraphContainer
    /// associated with this Job.
    /// \return A reference to the \ref Workspace ancestor of this Job, if this instance is valid
    /// (see \ref BifrostGraph::Executor::Job::isValid); an invalid \ref Workspace otherwise.
    /// \{
    const Workspace& getWorkspace() const noexcept;
    Workspace&       getWorkspace() noexcept;
    /// \}

    /// \brief Set whether runtime logging should be enabled when executing the job.
    /// During a job execution, some operators may report messages to the Amino::RuntimeServices.
    /// If the runtime logging is disabled, those messages will not be reported to the Workspace.
    /// \param [in] enable The desired state of runtime logging.
    void enableRuntimeLogging(bool enable) noexcept;

    /// \brief Query whether or not runtime logging is enabled when executing the job.
    /// \return true if runtime logging is enabled; false otherwise.
    /// \see enableRuntimeLogging
    bool isRuntimeLoggingEnabled() const noexcept;

    /// \brief Get the Job inputs.
    ///
    /// For each Job input, its value can be set using \ref Job::setInputValue, and then
    /// the graph can be executed using \ref Job::execute.
    ///
    /// \return A collection of inputs.
    ///
    /// \note The GraphContainer needs to be compiled (see \ref GraphContainer::compile) for the
    /// inputs to be valid, and they will remain valid until another graph is set (see \ref
    /// GraphContainer::setGraph) or until the next compilation.
    const Inputs& getInputs() const noexcept;

    /// \brief Set the given Job input value.
    ///
    /// This method allows one to manually set the value of a Job \p input obtained from
    /// \ref Job::getInputs.
    ///
    /// When a Job input value is set, it is converted from a host data by calling
    /// \ref TypeTranslation::convertValueFromHost on the \ref TypeTranslation shared library
    /// that has been registered for the type of this input.
    ///
    /// If a Job input value is not manually set before \ref Job::execute is called, its default
    /// value (coming from the graph, if any) will be used (see \ref Job::Input::defaultValue).
    ///
    /// \param [in] input The Job input.
    /// \param [in] valueData The host data that will be passed to
    /// \ref TypeTranslation::convertValueFromHost.
    /// \return true if the input has been successfully set; false otherwise.
    bool setInputValue(const Input& input, const TypeTranslation::ValueData* valueData) noexcept;

    /// \brief Execute the job with current inputs.
    ///
    /// Each Job input value is consumed by the execution and needs to be set prior to the next
    /// execution (see \ref Job::getInputs and \ref Job::setInputValue).
    ///
    /// \param [in] mode The mode on how to execute the job (see \ref JobExecutionMode).
    /// \return The job execution status (see \ref JobExecutionStatus).
    ///
    /// \note The GraphContainer needs to be compiled (see \ref GraphContainer::compile) for the job
    /// to be executable.
    ///
    /// \warning If the Job is executed asynchronously (for example, calling execute from a
    /// separate thread), no changes may be made to the GraphContainer that owns this Job while
    /// this execution is taking place (e.g. no change like a call to \ref GraphContainer::setGraph,
    /// to \ref Workspace::deleteGraphContainer, or even deleting the Workspace that owns the
    /// GraphContainer).
    JobExecutionStatus execute(JobExecutionMode mode = JobExecutionMode::kDefault) noexcept;

    /// \brief Get the Job outputs.
    ///
    /// Once the graph has been compiled, and the Job input values have been set (see \ref
    /// Job::getInputs and \ref Job::setInputValue), and the Job has been executed (see \ref
    /// Job::execute), then the value of each Job output can be retrieved using \ref
    /// Job::getOutputValue.
    ///
    /// \return A collection of outputs.
    ///
    /// \note The GraphContainer needs to be compiled (see \ref GraphContainer::compile) for the
    /// outputs to be valid, and they will remain valid until another graph is set (see \ref
    /// GraphContainer::setGraph) or until the next compilation.
    const Outputs& getOutputs() const noexcept;

    /// \brief Retrieve the given Job output value.
    ///
    /// This method allows one to retrieve the value of a Job \p output obtained from
    /// \ref Job::getOutputs.
    ///
    /// When a Job output value is retrieved, it is converted to a host data by calling
    /// \ref TypeTranslation::convertValueToHost on the \ref TypeTranslation shared library that
    /// has been registered for the type of this output.
    ///
    /// \param [in]     output    The Job output.
    /// \param [in,out] valueData The host data that will be passed to
    /// \ref TypeTranslation::convertValueToHost.
    /// \return true if the output has been successfully retrieved; false otherwise.
    bool getOutputValue(const Output& output, TypeTranslation::ValueData* valueData) const noexcept;

    //---------------------------------------------------------------------------------------------
    // IRestrictedJobServices
    //---------------------------------------------------------------------------------------------

    /// \brief Obtain an interface giving access to private Job services.
    /// \pre This Job must be valid (\ref BifrostGraph::Executor::Job::isValid).
    /// \return A reference to the IRestrictedJobServices interface of this Job.
    /// \{
    const Private::IRestrictedJobServices& getRestrictedServices() const noexcept;
    Private::IRestrictedJobServices&       getRestrictedServices() noexcept;
    /// \}

private:
    /// Disabled
    /// \{
    Job(const Job&)            = delete;
    Job(Job&&)                 = delete;
    Job& operator=(const Job&) = delete;
    Job& operator=(Job&&)      = delete;
    /// \}

private:
    Internal::PropagateConstPtr<Private::JobImpl, Internal::Owned::kYes> m_impl;
    static Job                                                           g_invalid;
};

} // namespace Executor
} // namespace BifrostGraph

#endif // BIFROSTGRAPH_EXECUTOR_JOB_H
