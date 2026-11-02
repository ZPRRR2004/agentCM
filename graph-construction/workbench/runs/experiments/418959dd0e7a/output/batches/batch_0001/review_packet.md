# 第 1 批 Predicate Discovery 结果

## 一、批次信息

处理 Window：1–5
Prompt 版本：v0001
本批新增谓词：53
本批已有谓词修订：0
当前谓词总数：53

## 二、本批新增谓词

### IS_EXECUTION_PLAN

签名：`IS_EXECUTION_PLAN(reasoning: reasoning)`

The reasoning explicitly expresses an intended future action or ordered sequence of actions that the agent intends to perform next in service of the task.

参数：

- `reasoning: reasoning`：The agent text expressing the intended future action(s) or the plan to be carried out.

成立条件：

- The reasoning explicitly names at least one action that is still to be performed (e.g., inspecting a file, listing a workspace, compiling an artifact, verifying a result).
- The intended action is presented as the agent's own next step, not as a hypothetical or rejected alternative.

排除条件：

- Merely reporting actions that have already been completed does not constitute a plan.
- Restating the user's task requirements without committing to a next action is not a plan.
- Post-hoc summarization of finished work is not a plan.

### IDENTIFIES_DEFECT_IN_OBSERVED_CONTENT

签名：`IDENTIFIES_DEFECT_IN_OBSERVED_CONTENT(reasoning: reasoning, observation: observation)`

The reasoning analyzes the content returned by an observation and pinpoints a concrete deficiency in that content that must be corrected for the task to succeed.

参数：

- `reasoning: reasoning`：The agent text performing the analysis and naming the deficiency.
- `observation: observation`：The earlier observation whose returned content contains the deficient artifact.

成立条件：

- The observation returns the actual content of an artifact (e.g., source text of a file) rather than mere metadata.
- The reasoning names specific missing, incomplete, or erroneous portions of that content (e.g., unresolved holes, absent steps, absent branches), rather than describing the content in general terms.

排除条件：

- The reasoning only restates or quotes the observed content without locating a deficiency.
- The reasoning discusses the artifact without any content from an observation having been supplied.
- The observation reports a tool failure rather than artifact content.

### GUIDES_ACTION_CONTENT

签名：`GUIDES_ACTION_CONTENT(reasoning: reasoning, action: action)`

The reasoning specifies the concrete content or form of an operation that a subsequent action then carries out, so that the action's payload is traceable to the reasoning.

参数：

- `reasoning: reasoning`：The agent text that decides what the operation should do or which content it should supply.
- `action: action`：The action that performs the operation whose content corresponds to the reasoning.

成立条件：

- The reasoning states a concrete intended operation or the concrete content to be produced (e.g., the exact replacement text, the exact command form).
- The action's payload matches that stated intent in substance, not merely in topic.
- The reasoning precedes the action.

排除条件：

- The reasoning only expresses a general goal while the action's content is fixed by a prior observation or by chance.
- The action diverges from what the reasoning specified.
- The reasoning is written after the action and only reports it.

### REPLACES_DEFECTIVE_CONTENT_OBSERVED

签名：`REPLACES_DEFECTIVE_CONTENT_OBSERVED(action: action, observation: observation)`

A modification action rewrites the very resource whose deficient content was reported by an earlier observation, supplying content that fills the identified gap.

参数：

- `action: action`：The modification action that writes or edits the resource.
- `observation: observation`：The earlier observation that returned the deficient content of that same resource.

成立条件：

- The observation returns content of a specific named resource (e.g., a file path) that lacks required elements.
- The action targets that same resource and supplies the content that was missing, replacing the deficient portion.
- The action precedes any confirmation of the resource's corrected state.

排除条件：

- The action targets a different resource than the one observed.
- The action is read-only or only inspects the resource.
- The observation is unrelated to the resource being written.

### CHECKS_TOOL_AVAILABILITY

签名：`CHECKS_TOOL_AVAILABILITY(action: action)`

The action queries whether a required tool or toolchain executable is present and usable, as a precondition check before performing the primary task.

参数：

- `action: action`：The action invoking a presence or version query on the required tool.

成立条件：

- The invocation resolves the location of the executable or asks the tool for its version, rather than performing the primary task.
- The stated intent or surrounding reasoning links the check to a tool needed for the primary task.

排除条件：

- The action performs the primary task itself (e.g., running the compiler on the target artifact).
- The action queries an unrelated utility or an unrelated property of the environment.

### PERFORMS_PRIMARY_BUILD

签名：`PERFORMS_PRIMARY_BUILD(action: action)`

The action executes the build or compilation step on the target artifact as the main operation of the task, rather than checking prerequisites or inspecting outputs.

参数：

- `action: action`：The action running the build/compilation command on the target artifact.

成立条件：

- The command invokes the build tool on the target artifact path.
- The command optionally combines the build with listing of produced outputs in the same invocation.

排除条件：

- The action only queries tool availability or version.
- The action only loads or prints an already compiled artifact for inspection.
- The action only reads source text without building.

### INDICATES_SUCCESSFUL_BUILD_WITH_ARTIFACT

签名：`INDICATES_SUCCESSFUL_BUILD_WITH_ARTIFACT(observation: observation)`

The observation resulting from a build or compilation command provides evidence that the build succeeded and that the compiled output artifact was produced.

参数：

- `observation: observation`：The observation returning the build command's output.

成立条件：

- The observation is the result of a build/compilation invocation.
- The output contains no error indication and evidences the compiled output artifact, such as by listing it or a success marker.

排除条件：

- The output contains compiler errors or a nonzero exit indication.
- The output merely lists files without any build having been executed.
- The output comes from a verification or inspection command rather than a build.

### IS_INVOCATION_ERROR_OBSERVATION

签名：`IS_INVOCATION_ERROR_OBSERVATION(observation: observation)`

The observation reports an error caused by the malformed or misinterpreted form of the tool invocation, rather than by a defect in the artifact being processed.

参数：

- `observation: observation`：The observation returning the failing tool output.

成立条件：

- The observation is marked as an error or shows a nonzero exit.
- The error message describes the tool's inability to interpret or locate something according to its argument convention (e.g., it looked for a file name derived from the supplied argument).

排除条件：

- The error indicates that the processed artifact itself is invalid or failed verification.
- The error reports an unavailable required tool or missing dependency.
- The observation reports success.

### CORRECTS_FAILED_INVOCATION

签名：`CORRECTS_FAILED_INVOCATION(retry_action: action, failure_observation: observation)`

A retry action pursues the same verification or inspection goal as a failed invocation while changing precisely the aspect of the invocation that the error identified.

参数：

- `retry_action: action`：The action that re-attempts the operation after the failure.
- `failure_observation: observation`：The earlier observation reporting the invocation error.

成立条件：

- The failure observation precedes the retry action, and the retry action targets the same overall goal.
- The retry action's parameters differ from the failed invocation in exactly the respect the error message indicated.
- The retry preserves the underlying resource being inspected or verified.

排除条件：

- The retry repeats the identical invocation that already failed.
- The action abandons the goal and does something unrelated.
- The action changes the artifact rather than the invocation form.

### CONFIRMS_CORRECTED_VERIFICATION

签名：`CONFIRMS_CORRECTED_VERIFICATION(retry_action: action, failure_observation: observation, confirmation_observation: observation)`

A retry action addresses a specific invocation failure, and a later observation establishes that the intended verification result was obtained.

参数：

- `retry_action: action`：The action attempting to fix the failed invocation.
- `failure_observation: observation`：The earlier observation reporting the invocation failure.
- `confirmation_observation: observation`：The later observation showing the intended verification output.

成立条件：

- The failure observation precedes the retry action, and the retry action corrects the identified invocation problem.
- The confirmation observation follows the retry action and contains the sought result (e.g., the queried declaration printed with its full content) without error.

排除条件：

- The retry is performed without any later observation demonstrating the sought result.
- The later observation still reports an error or an empty/irrelevant result.
- The later observation confirms something other than the failure's subject.

### ATTEMPTS_ARTIFACT_CONTENT_VERIFICATION

签名：`ATTEMPTS_ARTIFACT_CONTENT_VERIFICATION(action: action)`

The action attempts to inspect the semantic content of an already produced compiled artifact by loading it or querying a declaration from it, rather than by rebuilding it or reading raw bytes.

参数：

- `action: action`：The action that attempts to load the compiled artifact or query a declaration from it.

成立条件：

- The invocation attempts to load a compiled artifact into the tool's environment or asks the tool to print/check a named declaration.
- The action is distinct from the build that produced the artifact and from file-listing or byte-level inspection.

排除条件：

- The action rebuilds the artifact from source.
- The action only lists files or checks file sizes/timestamps.
- The action reads source text instead of the compiled artifact.

### ASSERTS_TASK_COMPLETION_WITH_EVIDENCE

签名：`ASSERTS_TASK_COMPLETION_WITH_EVIDENCE(reasoning: reasoning)`

The reasoning declares the overall task finished and backs the claim by citing the concrete artifacts produced and the verifications performed.

参数：

- `reasoning: reasoning`：The agent text concluding the task and citing its supporting evidence.

成立条件：

- The reasoning explicitly states that the task is complete or that all required steps are done.
- It references the concrete produced artifacts and the checks that were run to establish success.

排除条件：

- The reasoning describes an intermediate step or an open problem rather than final completion.
- The claim of completion cites no produced artifact or verification result.
- The reasoning admits that a required verification is still missing or failing.

### ANTICIPATES_FAILURE_MODE

签名：`ANTICIPATES_FAILURE_MODE(reasoning: reasoning)`

The reasoning predicts a specific failure mechanism that a default or naive configuration would produce, and explains how that mechanism leads to the failure, before any such failure has been observed.

参数：

- `reasoning: reasoning`：The agent text predicting a concrete failure mechanism and its consequence.

成立条件：

- The reasoning names a concrete failure mode that could arise from a default or naive setup, such as an account locked for key authentication, a commit finding no changes to record, stale deployed content preventing a later push, or a service unable to start without a supervisor.
- The reasoning explains the causal mechanism by which the default behavior produces that failure.
- The prediction is made before any observation in the trajectory reports that failure.

排除条件：

- The text reacts to a failure that has already been observed in a tool result.
- The text offers only generic caution or best-practice advice without identifying a specific failure mechanism.
- The text predicts a failure that is unrelated to the configuration being implemented.

### DERIVES_ENVIRONMENT_CONSTRAINT

签名：`DERIVES_ENVIRONMENT_CONSTRAINT(reasoning: reasoning, observation: observation)`

The reasoning interprets the content of a prior observation to establish a capability, absence, or structural constraint of the environment that conditions the chosen approach.

参数：

- `reasoning: reasoning`：The agent text drawing a capability or constraint conclusion from observed environment state.
- `observation: observation`：The earlier tool result whose content supplies the environment facts being interpreted.

成立条件：

- The reasoning states at least one specific environment fact that is traceable to the content of the observation, such as available or missing tools, package-manager reachability, process supervision model, user accounts, or filesystem layout.
- The reasoning treats that fact as a constraint or enabler that affects how the agent proceeds.

排除条件：

- The reasoning merely repeats or paraphrases the raw observation without drawing a constraint or capability conclusion.
- The observation only confirms that a command ran successfully and supplies no environment fact.
- The nodes are merely temporally adjacent or topically similar.

### ALIGNS_PROVISIONED_NAMES_WITH_REQUEST

签名：`ALIGNS_PROVISIONED_NAMES_WITH_REQUEST(action: action)`

The action creates or registers a named resource such as an account, filesystem path, hostname mapping, or listening endpoint under the exact identifier that the requester's unmodified commands will address, so those commands resolve to the provisioned resource.

参数：

- `action: action`：The provisioning action that establishes a named resource and fixes its identifier.

成立条件：

- The action establishes a named resource such as a user account, repository path, local hostname entry, or service listening endpoint.
- The identifier chosen in the action equals the identifier appearing in the requester's commands, such as an account name, repository path, host alias, or port number.

排除条件：

- The resource is created under an arbitrary or default identifier unrelated to the requester's commands.
- The chosen identifier differs from the requested one or would require the requester to alter the commands.
- The action only installs or inspects software without fixing the name of a resource.

### INSTALLS_MISSING_DEPENDENCIES

签名：`INSTALLS_MISSING_DEPENDENCIES(action: action, reasoning: reasoning)`

The action installs software packages that provide capabilities which the reasoning had identified as absent from the environment, and the installation occurs before the first attempt to use those capabilities.

参数：

- `action: action`：The package installation action supplying the absent capabilities.
- `reasoning: reasoning`：The agent text that identified the specific capabilities as missing.

成立条件：

- The reasoning records specific tools or services as absent or unusable in the environment.
- The action installs packages that provide those tools or services.
- The installation occurs before any action that depends on them.

排除条件：

- Packages are installed without any preceding identification of a gap.
- The gap is identified but no installation is attempted within the window.
- The action only refreshes or inspects package metadata without installing.

### MITIGATES_ANTICIPATED_PITFALL

签名：`MITIGATES_ANTICIPATED_PITFALL(action: action, reasoning: reasoning)`

The action applies a concrete countermeasure, visible in its own arguments, that prevents a specific failure mechanism the reasoning had predicted for a default or naive configuration.

参数：

- `action: action`：The action whose arguments contain the countermeasure.
- `reasoning: reasoning`：The earlier agent text predicting the failure mechanism that the countermeasure addresses.

成立条件：

- The reasoning predicts a specific failure mechanism for the default or naive configuration.
- The action contains an explicit flag, option, marker, permission setting, configuration directive, or resolution entry that directly prevents that mechanism.
- The correspondence between the countermeasure and the predicted mechanism is traceable by content, not merely by topic or proximity.

排除条件：

- The action performs only a generic implementation step with no countermeasure in its arguments.
- The action's arguments do not reference the predicted failure mechanism.
- The reasoning mentions a risk without prescribing or implying any countermeasure.

### WRITES_SERVICE_CONFIGURATION

签名：`WRITES_SERVICE_CONFIGURATION(action: action)`

The action creates or replaces the configuration of a service itself, so that when the service starts it exposes a specified listening endpoint and serves a specified directory or resource root.

参数：

- `action: action`：The file-write action that authors the service's own configuration.

成立条件：

- The write targets a configuration path belonging to a server or daemon.
- The written content specifies a listen address or port and a served root directory or resource root.

排除条件：

- The write targets application content, a deployment script, or an unrelated file rather than the service's own configuration.
- The written content does not specify an endpoint or a served root.
- The action only restarts or validates a service without authoring its configuration.

### AUTHORS_PUSH_DEPLOY_HOOK

签名：`AUTHORS_PUSH_DEPLOY_HOOK(action: action)`

The action writes an executable hook script that is triggered when a repository receives pushes and that materializes the pushed revision into a separate working directory intended for serving.

参数：

- `action: action`：The file-write action producing the receive-side hook script.

成立条件：

- The script is written into a repository's hook location and marked executable.
- The script reads pushed references and checks out the pushed branch into a designated work tree distinct from the repository directory.

排除条件：

- The write produces a server configuration file rather than a receive-side hook.
- The script operates directly on the repository directory with no separate target work tree.
- The action performs a one-off manual checkout instead of installing a triggered script.

### MODIFIES_OBSERVED_CONFIGURATION

签名：`MODIFIES_OBSERVED_CONFIGURATION(action: action, observation: observation)`

The action rewrites or replaces a configuration file whose existing content was returned by an earlier observation, and the written content reflects directives seen in that observation.

参数：

- `action: action`：The write action that rewrites the previously observed configuration file.
- `observation: observation`：The earlier tool result that returned the file's existing content.

成立条件：

- The observation returned the actual content of a configuration file, not merely its presence or metadata.
- The action writes to that same path.
- The written content preserves or deliberately alters directives that were visible in the observed content.

排除条件：

- The action writes a file whose content was never observed.
- The observation only lists a directory or reports file metadata.
- The write targets a different path than the observed file.

### CONFIRMS_SERVICE_STARTED

签名：`CONFIRMS_SERVICE_STARTED(action: action, observation: observation)`

The observation establishes that a service whose launch the action invoked is actually running, providing post-launch evidence of successful startup rather than only configuration acceptance.

参数：

- `action: action`：The action that attempted to launch the service.
- `observation: observation`：The tool result reporting evidence of the launched service's running state.

成立条件：

- The observation contains process, PID, listener, or equivalent runtime evidence that the service launched by the action is running.
- The observation does not report a startup error for that service.
- The running service corresponds to the service whose launch the action invoked.

排除条件：

- Only configuration validation succeeds, with no runtime evidence that the service is running.
- Processes appear that were started outside the action in question.
- The output reports a configuration or startup error.

### WIRES_PUSH_TO_SERVED_ROOT

签名：`WIRES_PUSH_TO_SERVED_ROOT(hook_action: action, service_config_action: action, target_dir_action: action)`

Three actions jointly establish a deployment chain in which a receive hook checks pushed content out into a directory that a web service is configured to serve on a specified port, so that pushing commits makes that content retrievable over HTTP.

参数：

- `hook_action: action`：The action authoring the receive hook whose checkout target is the serving directory.
- `service_config_action: action`：The action configuring the web service's listen port and document root.
- `target_dir_action: action`：The action preparing the serving directory that the hook writes into.

成立条件：

- The checkout path used by the hook action matches the serving directory prepared by the target_dir_action.
- The document root in the service configuration action matches that same directory.
- The service configuration specifies a listening port for HTTP access.
- Each link of the chain is evidenced in the content of the respective action.

排除条件：

- The hook checkout path, prepared directory, and document root differ from one another.
- A web service is configured to serve a root that no hook populates.
- A hook checks content out but no service serves that location.
- Any of the three links is missing, so the chain would not deliver pushed content over HTTP.

### VALIDATES_SERVICE_CONFIGURATION

签名：`VALIDATES_SERVICE_CONFIGURATION(action: action, observation: observation)`

The action invokes a service's own configuration syntax or consistency check on its configuration files, and the observation reports that the configuration is valid.

参数：

- `action: action`：The tool invocation that runs the service-specific configuration validation routine.
- `observation: observation`：The tool result reporting the validation outcome for that service configuration.

成立条件：

- The action runs the service's own validation or test routine (e.g., a config-test flag or subcommand of the daemon) on its configuration before or alongside activation.
- The observation explicitly reports that the syntax or consistency of that configuration is valid or successful.

排除条件：

- The action only writes, starts, or restarts the service without running a configuration validity check.
- The observation reports a validation failure or does not address configuration validity.
- The check validates something other than the service's configuration (e.g., a repository or application setting).

### CONFIGURES_HOSTNAME_RESOLUTION

签名：`CONFIGURES_HOSTNAME_RESOLUTION(action: action)`

The action modifies the system's hostname-to-address resolution mapping so that a symbolic host name resolves to a chosen address for subsequent commands.

参数：

- `action: action`：The tool invocation that adds or updates the system name-resolution mapping.

成立条件：

- The action writes or updates a system name-resolution mapping, such as an entry in the hosts file.
- The written mapping associates a host name with a network address that subsequent commands use to reach a service.

排除条件：

- The action changes service-level virtual-host or server-name configuration rather than system hostname resolution.
- The action writes a file that does not affect name resolution.
- The action only reads the current name-resolution mapping.

### TESTS_AUTHENTICATED_REMOTE_ACCESS

签名：`TESTS_AUTHENTICATED_REMOTE_ACCESS(action: action, observation: observation)`

The action installs or supplies a credential for a target account and performs a remote login using that credential, and the observation confirms that the login authenticated as the intended identity.

参数：

- `action: action`：The tool invocation that provisions or installs the credential and attempts the remote login.
- `observation: observation`：The tool result reporting whether the authenticated remote access succeeded and as which identity.

成立条件：

- The action creates, installs, or supplies a credential (e.g., a key pair or token) for a remote login test.
- The action executes a remote access command using that credential.
- The observation reports a successful authenticated identity or authenticated session for the intended account.

排除条件：

- The action tests unauthenticated network reachability or only starts the login daemon.
- The action prepares credentials but performs no login attempt.
- The observation reports authentication failure, permission denial, or host verification failure.

### EXECUTES_END_TO_END_USER_WORKFLOW

签名：`EXECUTES_END_TO_END_USER_WORKFLOW(action: action)`

The action reproduces the requester's end-to-end workflow by running operations from multiple interacting stages of that workflow in sequence, rather than exercising a single component in isolation.

参数：

- `action: action`：The tool invocation that runs the multi-stage user workflow.

成立条件：

- The action includes operations belonging to at least two distinct stages of the requested workflow, such as producing and transmitting source-controlled content and retrieving content from the served endpoint.
- The stages interact through the components being configured, so the invocation exercises their integration rather than a single isolated component.

排除条件：

- The action performs only a single isolated check, such as a configuration syntax test, process listing, or port query.
- The action only starts services without exercising the user-facing workflow.
- The action only prepares files or configuration without running the workflow stages.

### DIAGNOSES_FAILURE_CAUSE

签名：`DIAGNOSES_FAILURE_CAUSE(reasoning: reasoning, observation: observation)`

The reasoning explains why a previously observed failure occurred by identifying the specific cause or mechanism responsible for it.

参数：

- `reasoning: reasoning`：The agent text explaining the failure.
- `observation: observation`：The earlier tool result reporting the failure.

成立条件：

- The reasoning refers to the failure reported by the observation.
- The reasoning identifies a causal explanation for the failure, such as an environment setting not carried into a subcommand, an ownership safety rule rejecting the operation, or a host verification rule blocking access.

排除条件：

- The reasoning merely restates or quotes the error without causal analysis.
- The reasoning plans a next action without explaining why the observed failure occurred.
- The explanation concerns a failure other than the one reported by the paired observation.

### ATTEMPTS_REPAIR_OBSERVED_FAILURE

签名：`ATTEMPTS_REPAIR_OBSERVED_FAILURE(action: action, observation: observation)`

The action attempts to correct a previously observed failure by changing the operational condition responsible for it, such as configuration, execution context, environment, or credentials, rather than repeating the failing operation unchanged.

参数：

- `action: action`：The corrective action being attempted.
- `observation: observation`：The earlier tool result reporting the failure to be corrected.

成立条件：

- The observation reports a failure that occurs before the action.
- The action changes an operational condition relevant to that failure rather than repeating the identical failing operation unchanged.

排除条件：

- The action is unrelated to the observed failure.
- The action simply repeats the same failing operation with no corrective change.
- The action only inspects or logs state without attempting a correction.

### CONFIRMS_REPAIR

签名：`CONFIRMS_REPAIR(repair: action, failure: observation, confirmation: observation)`

A repair action addresses an observed failure, and a later observation establishes that the same failure has been resolved.

参数：

- `repair: action`：The action attempting to repair the failure.
- `failure: observation`：The earlier observation reporting the failure.
- `confirmation: observation`：The later observation confirming that the failure has been resolved.

成立条件：

- The failure observation precedes the repair action, and the repair action changes a condition relevant to that failure.
- The confirmation observation occurs after the repair and reports success or a state inconsistent with the original failure, so the original failure is no longer reproduced.

排除条件：

- No later observation confirms resolution of the original failure.
- The later observation still reports the original failure or leaves the affected state unchanged.
- The later observation confirms only an unrelated operation.

### ATTEMPTS_TEST_STATE_CLEANUP

签名：`ATTEMPTS_TEST_STATE_CLEANUP(action: action)`

The action removes or resets artifacts created while testing the requested workflow, such as temporary credentials, test clones, test commits or branches, and test-deployed content, to return the persistent state toward its pre-test condition.

参数：

- `action: action`：The cleanup action targeting temporary test artifacts.

成立条件：

- The action targets artifacts created by the agent's own testing, such as test credentials, test clones, test branches or commits, or files deployed by a test push.
- The action includes operations intended to restore the persistent state used by the requested workflow, such as clearing repository references, emptying the served root, or resetting the credential file.

排除条件：

- The action removes ordinary runtime files unrelated to test artifacts.
- The action only inspects test artifacts without deleting or resetting them.
- The action deletes user data that was not produced by the agent's testing.

### RESTORES_PRISTINE_STATE

签名：`RESTORES_PRISTINE_STATE(action: action, observation: observation)`

A cleanup action removes or resets temporary test artifacts, and the observation confirms that the targeted resources are absent, empty, or reset, leaving the relevant resource in its pre-test state.

参数：

- `action: action`：The cleanup action that removes or resets temporary test artifacts.
- `observation: observation`：The later tool result confirming that the targeted resources are absent, empty, or reset.

成立条件：

- The action performs cleanup of temporary test artifacts.
- The observation shows the targeted artifacts absent, empty, or reset to their initial state, such as no remaining references, an empty served root, or an emptied credential file.

排除条件：

- The observation shows that targeted test artifacts or test commits remain.
- The observation reports that the cleanup operation itself failed and left the state unchanged.
- The observation does not address the state of the cleaned resources.

### INSTALLS_SERVICE_RECOVERY_HELPER

签名：`INSTALLS_SERVICE_RECOVERY_HELPER(action: action)`

The action creates a reusable helper that checks whether required service daemons are running and starts them when they are absent, so that service availability can be restored later without manual intervention.

参数：

- `action: action`：The tool invocation that writes or installs the service recovery helper.

成立条件：

- The action writes or installs a script or helper containing service liveness checks and commands that start the services when they are not running.
- The helper is intended to be invoked later to restore service availability.

排除条件：

- The action writes ordinary application content or static service configuration without liveness or restart logic.
- The action only starts services once without creating a reusable recovery helper.
- The action merely documents how to restart the services rather than installing an executable helper.

### CHECKS_LISTENING_PORTS

签名：`CHECKS_LISTENING_PORTS(action: action, observation: observation)`

The action inspects the system's socket or connection tables for designated service ports, and the observation reports whether those ports are in a listening state and on which interfaces.

参数：

- `action: action`：The tool invocation that queries socket or connection tables for the service ports.
- `observation: observation`：The tool result reporting listening state or bound interfaces for the inspected ports.

成立条件：

- The action queries socket or connection-table state filtered to the designated service ports.
- The observation reports listening state or bound addresses for those ports.

排除条件：

- The action checks only process existence without inspecting socket state.
- The observation reports no port or socket state.
- The query is not directed at the ports of the configured services.

### VERIFICATION_OBSERVES_EXPECTED_RESULT

签名：`VERIFICATION_OBSERVES_EXPECTED_RESULT(action: action, observation: observation)`

The action performs a verification step that exercises the configured behavior, and the resulting observation contains the specific expected output, content, or state that demonstrates that behavior.

参数：

- `action: action`：The verification step that exercises the behavior being checked.
- `observation: observation`：The tool result containing the expected output, content, or state.

成立条件：

- The action deliberately exercises the configured behavior to verify it, such as retrieving served content, performing a login, or querying the live state.
- The observation contains the specific expected value, content, or success marker, not merely a generic exit status, that demonstrates the verified behavior.

排除条件：

- The observation reports an error or an unexpected value.
- The observation reports only generic execution success without evidence of the expected behavior.
- The action only writes configuration, starts a service, or checks syntax without exercising the behavior.

### EXPLAINS_OBSERVED_ANOMALY

签名：`EXPLAINS_OBSERVED_ANOMALY(explanation: reasoning, anomalous_observation: observation)`

The reasoning gives a causal account of why a recorded observation returned an unexpected, empty, or otherwise puzzling result that is not itself an error, naming a concrete mechanism (tool or option semantics, symlink handling, process lifecycle) rather than treating the result as a failure of the underlying goal.

参数：

- `explanation: reasoning`：The agent text that accounts for the puzzling result.
- `anomalous_observation: observation`：The observation whose output was empty, missing, or contrary to expectation without reporting an error.

成立条件：

- The explanation explicitly refers to a result contained in the observation that deviated from expectation or left a property undetermined.
- The explanation identifies a concrete cause for that result, such as a command that does not follow symlinks, a shell lacking a numeric conversion function, or a non-reaping parent process.

排除条件：

- The reasoning merely restates or quotes the observation without a causal account.
- The reasoning only proposes the next action and gives no cause for the puzzling result.
- The referenced result is not present in the observation, so there is no traceable link between the two nodes.
- The observation reports a tool error or failing command; causal explanation of an error is a failure-diagnosis mechanism rather than an anomaly explanation.

### REVERIFIES_WITH_ALTERNATIVE_MECHANISM

签名：`REVERIFIES_WITH_ALTERNATIVE_MECHANISM(recheck_action: action, inconclusive_observation: observation)`

A prior observation left a system property undetermined or contradicted expectation without reporting an error, and the action re-establishes that same property through a different tool, option, or access path rather than repeating the original check.

参数：

- `recheck_action: action`：The action performing the alternative re-verification.
- `inconclusive_observation: observation`：The earlier check whose output was empty, ambiguous, or insufficient to settle the property.

成立条件：

- The prior observation failed to reveal a property that the agent expected or needed to know, for example because it produced no output.
- The action inspects the same system property using a different command, option, or access path than the earlier check.
- The differing technique is what makes the property observable.

排除条件：

- The action reruns the identical command with identical options, adding no new observability.
- The action inspects a different property than the one left undetermined.
- The earlier observation was conclusive, so the action is routine verification rather than alternative re-verification.
- The earlier observation reported a tool error; correcting a failed invocation is a distinct mechanism.

### RESOLVES_FUNCTIONAL_DOUBT_BY_PROBE

签名：`RESOLVES_FUNCTIONAL_DOUBT_BY_PROBE(doubt_reasoning: reasoning, probe_action: action, probe_result: observation)`

The reasoning raises doubt about whether an observed anomaly actually impairs a required capability, a probe action exercises exactly that capability, and the resulting observation demonstrates that the capability still works, providing grounds to dismiss the anomaly.

参数：

- `doubt_reasoning: reasoning`：The agent text expressing uncertainty about whether the anomaly breaks functionality.
- `probe_action: action`：The action that exercises the capability put in doubt.
- `probe_result: observation`：The observation reporting the outcome of the probe.

成立条件：

- The reasoning identifies an observed anomaly and questions whether it affects a required capability.
- The probe action directly exercises the capability that was questioned.
- The probe result shows the capability behaving successfully, providing grounds to treat the anomaly as harmless.

排除条件：

- The probe does not target the capability that was questioned.
- The probe result is failing, inconclusive, or unrelated to the doubt.
- No doubt about functionality is expressed; the probe is ordinary acceptance testing.

### VERIFIES_ENUMERATED_STATE_ITEMS

签名：`VERIFIES_ENUMERATED_STATE_ITEMS(checklist_reasoning: reasoning, inspection_action: action)`

The reasoning itemizes discrete facets of system state to be confirmed, and the action performs a read-only inspection that reads back those same facets in one pass.

参数：

- `checklist_reasoning: reasoning`：The agent text enumerating the specific facets to be confirmed.
- `inspection_action: action`：The read-only action that reads back the enumerated state facets.

成立条件：

- The reasoning lists multiple discrete facets to confirm, such as services, listening ports, ownership or permissions, repository references, configuration contents, and endpoint status.
- The action issues read-only commands covering those same facets.
- The facets checked by the action can be mapped onto the enumerated items.

排除条件：

- The action mutates state rather than reading it back.
- The action checks facets that were not enumerated, or the reasoning gives only a general goal without itemized facets.
- The reasoning enumerates items but the action addresses only one of them.

### PROVISIONS_DISPOSABLE_CREDENTIAL

签名：`PROVISIONS_DISPOSABLE_CREDENTIAL(provisioning_action: action)`

The action creates transient authentication material in a temporary location and installs it into the authentication path solely so that the login or authentication flow can be exercised during testing, without intending it as the end user's credential.

参数：

- `provisioning_action: action`：The action generating and installing the temporary credential.

成立条件：

- The action generates authentication material such as a key pair or token at a temporary path.
- The generated material is placed into the authentication path, such as an authorized-keys file, so that a test login can succeed.
- The material is distinct from the credential the end user is expected to configure.

排除条件：

- The action sets up the credential the end user will keep and use.
- The action only reads or inspects existing credentials without generating new material.
- Generated material is intended for permanent production use rather than a test of the authentication path.

### REPLICATES_DOCUMENTED_USER_COMMANDS

签名：`REPLICATES_DOCUMENTED_USER_COMMANDS(sequence_reasoning: reasoning, replay_action: action)`

The reasoning lays out the exact command sequence the requester is expected to run, and the action executes that same sequence verbatim against the configured system in a fresh working location as an acceptance replay of the requester's workflow.

参数：

- `sequence_reasoning: reasoning`：The agent text enumerating the expected command sequence.
- `replay_action: action`：The action executing the documented command sequence.

成立条件：

- The reasoning enumerates the specific commands the requester will run, in order.
- The action executes those same commands, in the same order, rather than ad-hoc equivalents.
- The execution occurs in a clean location so the result reflects the requester's starting conditions.

排除条件：

- The action uses substitute commands that only approximate the documented workflow.
- The reasoning states general verification goals without listing a concrete command sequence.
- The action executes only a fragment of the documented sequence.

### INSTALLS_STARTUP_HOOK

签名：`INSTALLS_STARTUP_HOOK(hook_action: action)`

The action modifies shell startup configuration so that a previously created helper is invoked automatically on future login or interactive shells, wiring the helper into the session lifecycle.

参数：

- `hook_action: action`：The action writing or appending the helper invocation into startup files.

成立条件：

- The action writes to shell startup configuration, such as a profile directory file or a shell rc file.
- The written content invokes a named helper, for example by its script path, so that it runs on subsequent shells.
- The invocation is written in a failure-tolerant form that does not disturb the session.

排除条件：

- The action only creates the helper file without wiring it into startup configuration.
- The startup file is edited for unrelated purposes such as environment variables, aliases, or PATH, with no helper invocation.
- The invocation is written into a one-off command rather than persistent startup configuration.

### REUSES_ARTIFACT_CREATED_BY_EARLIER_ACTION

签名：`REUSES_ARTIFACT_CREATED_BY_EARLIER_ACTION(consumer_action: action, producer_action: action)`

An artifact such as a file, script, credential, or directory produced by one action is consumed as an operational input by a later action, creating a traceable cross-action dependency on that produced value.

参数：

- `consumer_action: action`：The later action whose command references the produced artifact.
- `producer_action: action`：The earlier action that created the artifact.

成立条件：

- The producer action creates a file, script, credential, or path at a specific location.
- The consumer action's command references that same location as an operational input, for example as a key path or a generated script path.
- The producer precedes the consumer, and no other node supplies the artifact.

排除条件：

- Both actions merely reference an artifact that pre-existed and was not created by the producer.
- The consumer action mentions the path only in narration without using it operationally.
- The artifact was created by an action outside the compared pair.

### CONFIRMS_DEPLOYMENT_PIPELINE

签名：`CONFIRMS_DEPLOYMENT_PIPELINE(publish_action: action, retrieval_action: action, served_result: observation)`

A publishing action successfully writes content into the configured deployment source, and a subsequent retrieval action reads that content back through the serving endpoint, with the result showing that the published content is actually being served.

参数：

- `publish_action: action`：The action that commits, pushes, or installs content into the repository or deployment source.
- `retrieval_action: action`：The action that fetches the content through the serving endpoint.
- `served_result: observation`：The observation reporting the retrieved content and the server response.

成立条件：

- The publishing action reports success in writing the content to the deployment source.
- The retrieval action addresses the serving endpoint that is supposed to expose that content after deployment.
- The served result contains the published content with a success status, showing that the publish-to-serve path works end to end.

排除条件：

- The retrieval occurs before the publishing action succeeds, so the served result cannot stem from that deployment.
- The served content differs from what was published.
- The retrieval reads a local copy or the repository directly rather than the serving endpoint.

### DETECTS_SOURCE_CONTENT_MISMATCH

签名：`DETECTS_SOURCE_CONTENT_MISMATCH(reasoning: reasoning)`

The reasoning identifies that the content returned from a data source does not correspond to that source's declared or expected identity, by comparing source-level labels with identifiers or structure present in the returned content.

参数：

- `reasoning: reasoning`：The agent text identifying the mismatch between the declared source identity and the returned content.

成立条件：

- The reasoning compares a source's declared label, such as its file name or requested identity, with identifiers or structure present in the returned content.
- The reasoning states that the content actually corresponds to a different identity than the declared source.

排除条件：

- The reasoning only parses or summarizes the returned content without claiming an identity mismatch.
- The discrepancy is incidental formatting rather than a conflict between declared and observed source identity.
- The reasoning merely reports that a tool call returned an error.

### RESOLVES_SOURCE_IDENTITY_AMBIGUITY

签名：`RESOLVES_SOURCE_IDENTITY_AMBIGUITY(reasoning: reasoning)`

The reasoning addresses conflicting or ambiguous source identities by considering the plausible mappings of the supplied data and adopting an interpretation whose conclusions hold under all of them, instead of committing to a single unverified mapping.

参数：

- `reasoning: reasoning`：The agent text resolving the ambiguity in source identity or data mapping.

成立条件：

- The reasoning makes the ambiguity explicit by considering at least two plausible mappings or interpretations of the supplied data.
- The reasoning adopts an interpretation or course of action whose result is invariant across those mappings, so the ambiguity no longer affects the task outcome.

排除条件：

- The reasoning selects one mapping without considering alternatives.
- The reasoning notes the ambiguity but takes no position that resolves it for the task.
- The reasoning merely restates the identity mismatch without drawing any consequence for how to proceed.

### DERIVES_SOLUTION_FROM_OBSERVED_DATA

签名：`DERIVES_SOLUTION_FROM_OBSERVED_DATA(reasoning: reasoning, observations: observation[])`

The reasoning derives a candidate solution by extracting structured data from the payloads of observations and combining those extracted values in a computation or selection.

参数：

- `reasoning: reasoning`：The reasoning that analyzes the observation payloads and derives the candidate solution.
- `observations: observation[]`：The observations whose returned payloads are jointly analyzed to derive the candidate solution.

成立条件：

- The reasoning extracts specific values, records, events, or constraints from the content returned by the observations.
- The candidate solution depends on the collective payload content of the observations rather than on their success status alone.
- The reasoning computes or selects the candidate solution from those extracted values.

排除条件：

- The observations are used only to confirm that an action succeeded.
- The candidate solution is stated without using the observation payload data as operational input.
- The reasoning only draws a general environment constraint from a single observation rather than deriving a solution.

### PROPOSES_CONCRETE_SOLUTION

签名：`PROPOSES_CONCRETE_SOLUTION(reasoning: reasoning)`

The reasoning states a specific, directly implementable solution or selection, such as a concrete value, configuration, or chosen item, rather than only describing requirements, criteria, or a search process.

参数：

- `reasoning: reasoning`：The agent text proposing the concrete solution or selection.

成立条件：

- The reasoning identifies at least one concrete value, item, configuration, or outcome that constitutes the selected solution.
- The stated specificity is sufficient to implement or verify the solution directly.

排除条件：

- The reasoning only enumerates requirements, constraints, or candidate approaches without selecting one.
- The reasoning only restates a solution that was already implemented or observed rather than proposing it.

### IMPLEMENTS_SELECTED_SOLUTION

签名：`IMPLEMENTS_SELECTED_SOLUTION(solution_action: action, reasoning: reasoning)`

The action produces the task's deliverable artifact, and that artifact embodies the concrete solution previously selected in the reasoning.

参数：

- `solution_action: action`：The action that creates or modifies the deliverable artifact.
- `reasoning: reasoning`：The reasoning that selected the concrete solution.

成立条件：

- The reasoning states a concrete selected solution before the action.
- The artifact written or modified by the action contains the key values, structure, or decision of that selected solution.
- The artifact is the task's deliverable rather than auxiliary tooling, a test, or a diagnostic.

排除条件：

- The action creates a script, test, or diagnostic tool instead of the deliverable artifact.
- The reasoning contains only a general plan or multiple unselected options.
- The content of the action cannot be traced to the selected solution.

### CREATES_VERIFICATION_ARTIFACT

签名：`CREATES_VERIFICATION_ARTIFACT(verification_action: action, reasoning: reasoning)`

The action writes or rewrites a programmable artifact whose purpose is to automatically check another artifact or result against conditions specified in the reasoning.

参数：

- `verification_action: action`：The action creating or rewriting the verification artifact.
- `reasoning: reasoning`：The reasoning specifying the checks or validation procedure to be encoded.

成立条件：

- The reasoning specifies checks or validation steps to be performed.
- The action writes a script, test, or equivalent programmable artifact containing those checks.
- The verification artifact is separate from the solution artifact it inspects.

排除条件：

- The action creates the task's deliverable artifact rather than a verification tool.
- The action only runs an already existing check without creating or rewriting it.
- The reasoning only states that verification should happen without defining any check content.

### REPORTS_EXECUTION_FAILURE

签名：`REPORTS_EXECUTION_FAILURE(observation: observation)`

The observation indicates that an executed action or script did not complete successfully and supplies diagnostic evidence of the failure.

参数：

- `observation: observation`：The observation reporting failed execution or diagnostic error output.

成立条件：

- The observation is marked as an error or contains explicit failure output such as a traceback, error message, or failure summary.
- The failure concerns the execution of the invoked operation itself.

排除条件：

- The observation reports successful completion or normal output.
- The observation contains only a warning or an expected negative result.
- The observation reports an empty or unsuccessful search result that is a legitimate outcome of the operation rather than an execution failure.

### CONFIRMS_VERIFICATION_SUCCESS

签名：`CONFIRMS_VERIFICATION_SUCCESS(observation: observation)`

The observation reports that a validation procedure completed and that the conditions it was meant to check were satisfied.

参数：

- `observation: observation`：The observation reporting the successful validation result.

成立条件：

- The observation contains an explicit success statement or passing verdict for the validation.
- The reported result covers the conditions the validation was designed to check, not a single incidental assertion.

排除条件：

- The observation returns raw data, file contents, or a listing without any validation verdict.
- The observation reports a failing or only partially passing validation.

### PERFORMS_INTEGRITY_CHECK

签名：`PERFORMS_INTEGRITY_CHECK(action: action)`

The action inspects checksums, hashes, or modification metadata of named resources in order to establish whether protected inputs have remained unchanged.

参数：

- `action: action`：The action performing the integrity check.

成立条件：

- The action computes or retrieves checksums, hashes, sizes, or modification timestamps for named resources.
- The check is directed at confirming that those resources were not modified.

排除条件：

- The action merely reads or writes the content of the resources without inspecting integrity metadata.
- The action lists files for a purpose other than confirming that protected inputs are unchanged.

### PROVIDES_INTEGRITY_EVIDENCE

签名：`PROVIDES_INTEGRITY_EVIDENCE(observation: observation)`

The observation returns checksums, hashes, or comparable metadata for named resources that allows their modification state to be assessed.

参数：

- `observation: observation`：The observation providing integrity-relevant metadata for named resources.

成立条件：

- The observation contains integrity-relevant metadata such as checksums, hashes, sizes, or modification timestamps for named resources.
- The metadata is tied to specific named resources whose integrity is at issue.

排除条件：

- The observation contains only file contents, execution output, or success messages.
- The observation provides a bare directory listing with no integrity-relevant metadata.

## 三、本批已有谓词修订

本批没有修订已有谓词。

## 四、当前完整 Registry

### IS_EXECUTION_PLAN

签名：`IS_EXECUTION_PLAN(reasoning: reasoning)`

The reasoning explicitly expresses an intended future action or ordered sequence of actions that the agent intends to perform next in service of the task.

参数：

- `reasoning: reasoning`：The agent text expressing the intended future action(s) or the plan to be carried out.

成立条件：

- The reasoning explicitly names at least one action that is still to be performed (e.g., inspecting a file, listing a workspace, compiling an artifact, verifying a result).
- The intended action is presented as the agent's own next step, not as a hypothetical or rejected alternative.

排除条件：

- Merely reporting actions that have already been completed does not constitute a plan.
- Restating the user's task requirements without committing to a next action is not a plan.
- Post-hoc summarization of finished work is not a plan.

### IDENTIFIES_DEFECT_IN_OBSERVED_CONTENT

签名：`IDENTIFIES_DEFECT_IN_OBSERVED_CONTENT(reasoning: reasoning, observation: observation)`

The reasoning analyzes the content returned by an observation and pinpoints a concrete deficiency in that content that must be corrected for the task to succeed.

参数：

- `reasoning: reasoning`：The agent text performing the analysis and naming the deficiency.
- `observation: observation`：The earlier observation whose returned content contains the deficient artifact.

成立条件：

- The observation returns the actual content of an artifact (e.g., source text of a file) rather than mere metadata.
- The reasoning names specific missing, incomplete, or erroneous portions of that content (e.g., unresolved holes, absent steps, absent branches), rather than describing the content in general terms.

排除条件：

- The reasoning only restates or quotes the observed content without locating a deficiency.
- The reasoning discusses the artifact without any content from an observation having been supplied.
- The observation reports a tool failure rather than artifact content.

### GUIDES_ACTION_CONTENT

签名：`GUIDES_ACTION_CONTENT(reasoning: reasoning, action: action)`

The reasoning specifies the concrete content or form of an operation that a subsequent action then carries out, so that the action's payload is traceable to the reasoning.

参数：

- `reasoning: reasoning`：The agent text that decides what the operation should do or which content it should supply.
- `action: action`：The action that performs the operation whose content corresponds to the reasoning.

成立条件：

- The reasoning states a concrete intended operation or the concrete content to be produced (e.g., the exact replacement text, the exact command form).
- The action's payload matches that stated intent in substance, not merely in topic.
- The reasoning precedes the action.

排除条件：

- The reasoning only expresses a general goal while the action's content is fixed by a prior observation or by chance.
- The action diverges from what the reasoning specified.
- The reasoning is written after the action and only reports it.

### REPLACES_DEFECTIVE_CONTENT_OBSERVED

签名：`REPLACES_DEFECTIVE_CONTENT_OBSERVED(action: action, observation: observation)`

A modification action rewrites the very resource whose deficient content was reported by an earlier observation, supplying content that fills the identified gap.

参数：

- `action: action`：The modification action that writes or edits the resource.
- `observation: observation`：The earlier observation that returned the deficient content of that same resource.

成立条件：

- The observation returns content of a specific named resource (e.g., a file path) that lacks required elements.
- The action targets that same resource and supplies the content that was missing, replacing the deficient portion.
- The action precedes any confirmation of the resource's corrected state.

排除条件：

- The action targets a different resource than the one observed.
- The action is read-only or only inspects the resource.
- The observation is unrelated to the resource being written.

### CHECKS_TOOL_AVAILABILITY

签名：`CHECKS_TOOL_AVAILABILITY(action: action)`

The action queries whether a required tool or toolchain executable is present and usable, as a precondition check before performing the primary task.

参数：

- `action: action`：The action invoking a presence or version query on the required tool.

成立条件：

- The invocation resolves the location of the executable or asks the tool for its version, rather than performing the primary task.
- The stated intent or surrounding reasoning links the check to a tool needed for the primary task.

排除条件：

- The action performs the primary task itself (e.g., running the compiler on the target artifact).
- The action queries an unrelated utility or an unrelated property of the environment.

### PERFORMS_PRIMARY_BUILD

签名：`PERFORMS_PRIMARY_BUILD(action: action)`

The action executes the build or compilation step on the target artifact as the main operation of the task, rather than checking prerequisites or inspecting outputs.

参数：

- `action: action`：The action running the build/compilation command on the target artifact.

成立条件：

- The command invokes the build tool on the target artifact path.
- The command optionally combines the build with listing of produced outputs in the same invocation.

排除条件：

- The action only queries tool availability or version.
- The action only loads or prints an already compiled artifact for inspection.
- The action only reads source text without building.

### INDICATES_SUCCESSFUL_BUILD_WITH_ARTIFACT

签名：`INDICATES_SUCCESSFUL_BUILD_WITH_ARTIFACT(observation: observation)`

The observation resulting from a build or compilation command provides evidence that the build succeeded and that the compiled output artifact was produced.

参数：

- `observation: observation`：The observation returning the build command's output.

成立条件：

- The observation is the result of a build/compilation invocation.
- The output contains no error indication and evidences the compiled output artifact, such as by listing it or a success marker.

排除条件：

- The output contains compiler errors or a nonzero exit indication.
- The output merely lists files without any build having been executed.
- The output comes from a verification or inspection command rather than a build.

### IS_INVOCATION_ERROR_OBSERVATION

签名：`IS_INVOCATION_ERROR_OBSERVATION(observation: observation)`

The observation reports an error caused by the malformed or misinterpreted form of the tool invocation, rather than by a defect in the artifact being processed.

参数：

- `observation: observation`：The observation returning the failing tool output.

成立条件：

- The observation is marked as an error or shows a nonzero exit.
- The error message describes the tool's inability to interpret or locate something according to its argument convention (e.g., it looked for a file name derived from the supplied argument).

排除条件：

- The error indicates that the processed artifact itself is invalid or failed verification.
- The error reports an unavailable required tool or missing dependency.
- The observation reports success.

### CORRECTS_FAILED_INVOCATION

签名：`CORRECTS_FAILED_INVOCATION(retry_action: action, failure_observation: observation)`

A retry action pursues the same verification or inspection goal as a failed invocation while changing precisely the aspect of the invocation that the error identified.

参数：

- `retry_action: action`：The action that re-attempts the operation after the failure.
- `failure_observation: observation`：The earlier observation reporting the invocation error.

成立条件：

- The failure observation precedes the retry action, and the retry action targets the same overall goal.
- The retry action's parameters differ from the failed invocation in exactly the respect the error message indicated.
- The retry preserves the underlying resource being inspected or verified.

排除条件：

- The retry repeats the identical invocation that already failed.
- The action abandons the goal and does something unrelated.
- The action changes the artifact rather than the invocation form.

### CONFIRMS_CORRECTED_VERIFICATION

签名：`CONFIRMS_CORRECTED_VERIFICATION(retry_action: action, failure_observation: observation, confirmation_observation: observation)`

A retry action addresses a specific invocation failure, and a later observation establishes that the intended verification result was obtained.

参数：

- `retry_action: action`：The action attempting to fix the failed invocation.
- `failure_observation: observation`：The earlier observation reporting the invocation failure.
- `confirmation_observation: observation`：The later observation showing the intended verification output.

成立条件：

- The failure observation precedes the retry action, and the retry action corrects the identified invocation problem.
- The confirmation observation follows the retry action and contains the sought result (e.g., the queried declaration printed with its full content) without error.

排除条件：

- The retry is performed without any later observation demonstrating the sought result.
- The later observation still reports an error or an empty/irrelevant result.
- The later observation confirms something other than the failure's subject.

### ATTEMPTS_ARTIFACT_CONTENT_VERIFICATION

签名：`ATTEMPTS_ARTIFACT_CONTENT_VERIFICATION(action: action)`

The action attempts to inspect the semantic content of an already produced compiled artifact by loading it or querying a declaration from it, rather than by rebuilding it or reading raw bytes.

参数：

- `action: action`：The action that attempts to load the compiled artifact or query a declaration from it.

成立条件：

- The invocation attempts to load a compiled artifact into the tool's environment or asks the tool to print/check a named declaration.
- The action is distinct from the build that produced the artifact and from file-listing or byte-level inspection.

排除条件：

- The action rebuilds the artifact from source.
- The action only lists files or checks file sizes/timestamps.
- The action reads source text instead of the compiled artifact.

### ASSERTS_TASK_COMPLETION_WITH_EVIDENCE

签名：`ASSERTS_TASK_COMPLETION_WITH_EVIDENCE(reasoning: reasoning)`

The reasoning declares the overall task finished and backs the claim by citing the concrete artifacts produced and the verifications performed.

参数：

- `reasoning: reasoning`：The agent text concluding the task and citing its supporting evidence.

成立条件：

- The reasoning explicitly states that the task is complete or that all required steps are done.
- It references the concrete produced artifacts and the checks that were run to establish success.

排除条件：

- The reasoning describes an intermediate step or an open problem rather than final completion.
- The claim of completion cites no produced artifact or verification result.
- The reasoning admits that a required verification is still missing or failing.

### ANTICIPATES_FAILURE_MODE

签名：`ANTICIPATES_FAILURE_MODE(reasoning: reasoning)`

The reasoning predicts a specific failure mechanism that a default or naive configuration would produce, and explains how that mechanism leads to the failure, before any such failure has been observed.

参数：

- `reasoning: reasoning`：The agent text predicting a concrete failure mechanism and its consequence.

成立条件：

- The reasoning names a concrete failure mode that could arise from a default or naive setup, such as an account locked for key authentication, a commit finding no changes to record, stale deployed content preventing a later push, or a service unable to start without a supervisor.
- The reasoning explains the causal mechanism by which the default behavior produces that failure.
- The prediction is made before any observation in the trajectory reports that failure.

排除条件：

- The text reacts to a failure that has already been observed in a tool result.
- The text offers only generic caution or best-practice advice without identifying a specific failure mechanism.
- The text predicts a failure that is unrelated to the configuration being implemented.

### DERIVES_ENVIRONMENT_CONSTRAINT

签名：`DERIVES_ENVIRONMENT_CONSTRAINT(reasoning: reasoning, observation: observation)`

The reasoning interprets the content of a prior observation to establish a capability, absence, or structural constraint of the environment that conditions the chosen approach.

参数：

- `reasoning: reasoning`：The agent text drawing a capability or constraint conclusion from observed environment state.
- `observation: observation`：The earlier tool result whose content supplies the environment facts being interpreted.

成立条件：

- The reasoning states at least one specific environment fact that is traceable to the content of the observation, such as available or missing tools, package-manager reachability, process supervision model, user accounts, or filesystem layout.
- The reasoning treats that fact as a constraint or enabler that affects how the agent proceeds.

排除条件：

- The reasoning merely repeats or paraphrases the raw observation without drawing a constraint or capability conclusion.
- The observation only confirms that a command ran successfully and supplies no environment fact.
- The nodes are merely temporally adjacent or topically similar.

### ALIGNS_PROVISIONED_NAMES_WITH_REQUEST

签名：`ALIGNS_PROVISIONED_NAMES_WITH_REQUEST(action: action)`

The action creates or registers a named resource such as an account, filesystem path, hostname mapping, or listening endpoint under the exact identifier that the requester's unmodified commands will address, so those commands resolve to the provisioned resource.

参数：

- `action: action`：The provisioning action that establishes a named resource and fixes its identifier.

成立条件：

- The action establishes a named resource such as a user account, repository path, local hostname entry, or service listening endpoint.
- The identifier chosen in the action equals the identifier appearing in the requester's commands, such as an account name, repository path, host alias, or port number.

排除条件：

- The resource is created under an arbitrary or default identifier unrelated to the requester's commands.
- The chosen identifier differs from the requested one or would require the requester to alter the commands.
- The action only installs or inspects software without fixing the name of a resource.

### INSTALLS_MISSING_DEPENDENCIES

签名：`INSTALLS_MISSING_DEPENDENCIES(action: action, reasoning: reasoning)`

The action installs software packages that provide capabilities which the reasoning had identified as absent from the environment, and the installation occurs before the first attempt to use those capabilities.

参数：

- `action: action`：The package installation action supplying the absent capabilities.
- `reasoning: reasoning`：The agent text that identified the specific capabilities as missing.

成立条件：

- The reasoning records specific tools or services as absent or unusable in the environment.
- The action installs packages that provide those tools or services.
- The installation occurs before any action that depends on them.

排除条件：

- Packages are installed without any preceding identification of a gap.
- The gap is identified but no installation is attempted within the window.
- The action only refreshes or inspects package metadata without installing.

### MITIGATES_ANTICIPATED_PITFALL

签名：`MITIGATES_ANTICIPATED_PITFALL(action: action, reasoning: reasoning)`

The action applies a concrete countermeasure, visible in its own arguments, that prevents a specific failure mechanism the reasoning had predicted for a default or naive configuration.

参数：

- `action: action`：The action whose arguments contain the countermeasure.
- `reasoning: reasoning`：The earlier agent text predicting the failure mechanism that the countermeasure addresses.

成立条件：

- The reasoning predicts a specific failure mechanism for the default or naive configuration.
- The action contains an explicit flag, option, marker, permission setting, configuration directive, or resolution entry that directly prevents that mechanism.
- The correspondence between the countermeasure and the predicted mechanism is traceable by content, not merely by topic or proximity.

排除条件：

- The action performs only a generic implementation step with no countermeasure in its arguments.
- The action's arguments do not reference the predicted failure mechanism.
- The reasoning mentions a risk without prescribing or implying any countermeasure.

### WRITES_SERVICE_CONFIGURATION

签名：`WRITES_SERVICE_CONFIGURATION(action: action)`

The action creates or replaces the configuration of a service itself, so that when the service starts it exposes a specified listening endpoint and serves a specified directory or resource root.

参数：

- `action: action`：The file-write action that authors the service's own configuration.

成立条件：

- The write targets a configuration path belonging to a server or daemon.
- The written content specifies a listen address or port and a served root directory or resource root.

排除条件：

- The write targets application content, a deployment script, or an unrelated file rather than the service's own configuration.
- The written content does not specify an endpoint or a served root.
- The action only restarts or validates a service without authoring its configuration.

### AUTHORS_PUSH_DEPLOY_HOOK

签名：`AUTHORS_PUSH_DEPLOY_HOOK(action: action)`

The action writes an executable hook script that is triggered when a repository receives pushes and that materializes the pushed revision into a separate working directory intended for serving.

参数：

- `action: action`：The file-write action producing the receive-side hook script.

成立条件：

- The script is written into a repository's hook location and marked executable.
- The script reads pushed references and checks out the pushed branch into a designated work tree distinct from the repository directory.

排除条件：

- The write produces a server configuration file rather than a receive-side hook.
- The script operates directly on the repository directory with no separate target work tree.
- The action performs a one-off manual checkout instead of installing a triggered script.

### MODIFIES_OBSERVED_CONFIGURATION

签名：`MODIFIES_OBSERVED_CONFIGURATION(action: action, observation: observation)`

The action rewrites or replaces a configuration file whose existing content was returned by an earlier observation, and the written content reflects directives seen in that observation.

参数：

- `action: action`：The write action that rewrites the previously observed configuration file.
- `observation: observation`：The earlier tool result that returned the file's existing content.

成立条件：

- The observation returned the actual content of a configuration file, not merely its presence or metadata.
- The action writes to that same path.
- The written content preserves or deliberately alters directives that were visible in the observed content.

排除条件：

- The action writes a file whose content was never observed.
- The observation only lists a directory or reports file metadata.
- The write targets a different path than the observed file.

### CONFIRMS_SERVICE_STARTED

签名：`CONFIRMS_SERVICE_STARTED(action: action, observation: observation)`

The observation establishes that a service whose launch the action invoked is actually running, providing post-launch evidence of successful startup rather than only configuration acceptance.

参数：

- `action: action`：The action that attempted to launch the service.
- `observation: observation`：The tool result reporting evidence of the launched service's running state.

成立条件：

- The observation contains process, PID, listener, or equivalent runtime evidence that the service launched by the action is running.
- The observation does not report a startup error for that service.
- The running service corresponds to the service whose launch the action invoked.

排除条件：

- Only configuration validation succeeds, with no runtime evidence that the service is running.
- Processes appear that were started outside the action in question.
- The output reports a configuration or startup error.

### WIRES_PUSH_TO_SERVED_ROOT

签名：`WIRES_PUSH_TO_SERVED_ROOT(hook_action: action, service_config_action: action, target_dir_action: action)`

Three actions jointly establish a deployment chain in which a receive hook checks pushed content out into a directory that a web service is configured to serve on a specified port, so that pushing commits makes that content retrievable over HTTP.

参数：

- `hook_action: action`：The action authoring the receive hook whose checkout target is the serving directory.
- `service_config_action: action`：The action configuring the web service's listen port and document root.
- `target_dir_action: action`：The action preparing the serving directory that the hook writes into.

成立条件：

- The checkout path used by the hook action matches the serving directory prepared by the target_dir_action.
- The document root in the service configuration action matches that same directory.
- The service configuration specifies a listening port for HTTP access.
- Each link of the chain is evidenced in the content of the respective action.

排除条件：

- The hook checkout path, prepared directory, and document root differ from one another.
- A web service is configured to serve a root that no hook populates.
- A hook checks content out but no service serves that location.
- Any of the three links is missing, so the chain would not deliver pushed content over HTTP.

### VALIDATES_SERVICE_CONFIGURATION

签名：`VALIDATES_SERVICE_CONFIGURATION(action: action, observation: observation)`

The action invokes a service's own configuration syntax or consistency check on its configuration files, and the observation reports that the configuration is valid.

参数：

- `action: action`：The tool invocation that runs the service-specific configuration validation routine.
- `observation: observation`：The tool result reporting the validation outcome for that service configuration.

成立条件：

- The action runs the service's own validation or test routine (e.g., a config-test flag or subcommand of the daemon) on its configuration before or alongside activation.
- The observation explicitly reports that the syntax or consistency of that configuration is valid or successful.

排除条件：

- The action only writes, starts, or restarts the service without running a configuration validity check.
- The observation reports a validation failure or does not address configuration validity.
- The check validates something other than the service's configuration (e.g., a repository or application setting).

### CONFIGURES_HOSTNAME_RESOLUTION

签名：`CONFIGURES_HOSTNAME_RESOLUTION(action: action)`

The action modifies the system's hostname-to-address resolution mapping so that a symbolic host name resolves to a chosen address for subsequent commands.

参数：

- `action: action`：The tool invocation that adds or updates the system name-resolution mapping.

成立条件：

- The action writes or updates a system name-resolution mapping, such as an entry in the hosts file.
- The written mapping associates a host name with a network address that subsequent commands use to reach a service.

排除条件：

- The action changes service-level virtual-host or server-name configuration rather than system hostname resolution.
- The action writes a file that does not affect name resolution.
- The action only reads the current name-resolution mapping.

### TESTS_AUTHENTICATED_REMOTE_ACCESS

签名：`TESTS_AUTHENTICATED_REMOTE_ACCESS(action: action, observation: observation)`

The action installs or supplies a credential for a target account and performs a remote login using that credential, and the observation confirms that the login authenticated as the intended identity.

参数：

- `action: action`：The tool invocation that provisions or installs the credential and attempts the remote login.
- `observation: observation`：The tool result reporting whether the authenticated remote access succeeded and as which identity.

成立条件：

- The action creates, installs, or supplies a credential (e.g., a key pair or token) for a remote login test.
- The action executes a remote access command using that credential.
- The observation reports a successful authenticated identity or authenticated session for the intended account.

排除条件：

- The action tests unauthenticated network reachability or only starts the login daemon.
- The action prepares credentials but performs no login attempt.
- The observation reports authentication failure, permission denial, or host verification failure.

### EXECUTES_END_TO_END_USER_WORKFLOW

签名：`EXECUTES_END_TO_END_USER_WORKFLOW(action: action)`

The action reproduces the requester's end-to-end workflow by running operations from multiple interacting stages of that workflow in sequence, rather than exercising a single component in isolation.

参数：

- `action: action`：The tool invocation that runs the multi-stage user workflow.

成立条件：

- The action includes operations belonging to at least two distinct stages of the requested workflow, such as producing and transmitting source-controlled content and retrieving content from the served endpoint.
- The stages interact through the components being configured, so the invocation exercises their integration rather than a single isolated component.

排除条件：

- The action performs only a single isolated check, such as a configuration syntax test, process listing, or port query.
- The action only starts services without exercising the user-facing workflow.
- The action only prepares files or configuration without running the workflow stages.

### DIAGNOSES_FAILURE_CAUSE

签名：`DIAGNOSES_FAILURE_CAUSE(reasoning: reasoning, observation: observation)`

The reasoning explains why a previously observed failure occurred by identifying the specific cause or mechanism responsible for it.

参数：

- `reasoning: reasoning`：The agent text explaining the failure.
- `observation: observation`：The earlier tool result reporting the failure.

成立条件：

- The reasoning refers to the failure reported by the observation.
- The reasoning identifies a causal explanation for the failure, such as an environment setting not carried into a subcommand, an ownership safety rule rejecting the operation, or a host verification rule blocking access.

排除条件：

- The reasoning merely restates or quotes the error without causal analysis.
- The reasoning plans a next action without explaining why the observed failure occurred.
- The explanation concerns a failure other than the one reported by the paired observation.

### ATTEMPTS_REPAIR_OBSERVED_FAILURE

签名：`ATTEMPTS_REPAIR_OBSERVED_FAILURE(action: action, observation: observation)`

The action attempts to correct a previously observed failure by changing the operational condition responsible for it, such as configuration, execution context, environment, or credentials, rather than repeating the failing operation unchanged.

参数：

- `action: action`：The corrective action being attempted.
- `observation: observation`：The earlier tool result reporting the failure to be corrected.

成立条件：

- The observation reports a failure that occurs before the action.
- The action changes an operational condition relevant to that failure rather than repeating the identical failing operation unchanged.

排除条件：

- The action is unrelated to the observed failure.
- The action simply repeats the same failing operation with no corrective change.
- The action only inspects or logs state without attempting a correction.

### CONFIRMS_REPAIR

签名：`CONFIRMS_REPAIR(repair: action, failure: observation, confirmation: observation)`

A repair action addresses an observed failure, and a later observation establishes that the same failure has been resolved.

参数：

- `repair: action`：The action attempting to repair the failure.
- `failure: observation`：The earlier observation reporting the failure.
- `confirmation: observation`：The later observation confirming that the failure has been resolved.

成立条件：

- The failure observation precedes the repair action, and the repair action changes a condition relevant to that failure.
- The confirmation observation occurs after the repair and reports success or a state inconsistent with the original failure, so the original failure is no longer reproduced.

排除条件：

- No later observation confirms resolution of the original failure.
- The later observation still reports the original failure or leaves the affected state unchanged.
- The later observation confirms only an unrelated operation.

### ATTEMPTS_TEST_STATE_CLEANUP

签名：`ATTEMPTS_TEST_STATE_CLEANUP(action: action)`

The action removes or resets artifacts created while testing the requested workflow, such as temporary credentials, test clones, test commits or branches, and test-deployed content, to return the persistent state toward its pre-test condition.

参数：

- `action: action`：The cleanup action targeting temporary test artifacts.

成立条件：

- The action targets artifacts created by the agent's own testing, such as test credentials, test clones, test branches or commits, or files deployed by a test push.
- The action includes operations intended to restore the persistent state used by the requested workflow, such as clearing repository references, emptying the served root, or resetting the credential file.

排除条件：

- The action removes ordinary runtime files unrelated to test artifacts.
- The action only inspects test artifacts without deleting or resetting them.
- The action deletes user data that was not produced by the agent's testing.

### RESTORES_PRISTINE_STATE

签名：`RESTORES_PRISTINE_STATE(action: action, observation: observation)`

A cleanup action removes or resets temporary test artifacts, and the observation confirms that the targeted resources are absent, empty, or reset, leaving the relevant resource in its pre-test state.

参数：

- `action: action`：The cleanup action that removes or resets temporary test artifacts.
- `observation: observation`：The later tool result confirming that the targeted resources are absent, empty, or reset.

成立条件：

- The action performs cleanup of temporary test artifacts.
- The observation shows the targeted artifacts absent, empty, or reset to their initial state, such as no remaining references, an empty served root, or an emptied credential file.

排除条件：

- The observation shows that targeted test artifacts or test commits remain.
- The observation reports that the cleanup operation itself failed and left the state unchanged.
- The observation does not address the state of the cleaned resources.

### INSTALLS_SERVICE_RECOVERY_HELPER

签名：`INSTALLS_SERVICE_RECOVERY_HELPER(action: action)`

The action creates a reusable helper that checks whether required service daemons are running and starts them when they are absent, so that service availability can be restored later without manual intervention.

参数：

- `action: action`：The tool invocation that writes or installs the service recovery helper.

成立条件：

- The action writes or installs a script or helper containing service liveness checks and commands that start the services when they are not running.
- The helper is intended to be invoked later to restore service availability.

排除条件：

- The action writes ordinary application content or static service configuration without liveness or restart logic.
- The action only starts services once without creating a reusable recovery helper.
- The action merely documents how to restart the services rather than installing an executable helper.

### CHECKS_LISTENING_PORTS

签名：`CHECKS_LISTENING_PORTS(action: action, observation: observation)`

The action inspects the system's socket or connection tables for designated service ports, and the observation reports whether those ports are in a listening state and on which interfaces.

参数：

- `action: action`：The tool invocation that queries socket or connection tables for the service ports.
- `observation: observation`：The tool result reporting listening state or bound interfaces for the inspected ports.

成立条件：

- The action queries socket or connection-table state filtered to the designated service ports.
- The observation reports listening state or bound addresses for those ports.

排除条件：

- The action checks only process existence without inspecting socket state.
- The observation reports no port or socket state.
- The query is not directed at the ports of the configured services.

### VERIFICATION_OBSERVES_EXPECTED_RESULT

签名：`VERIFICATION_OBSERVES_EXPECTED_RESULT(action: action, observation: observation)`

The action performs a verification step that exercises the configured behavior, and the resulting observation contains the specific expected output, content, or state that demonstrates that behavior.

参数：

- `action: action`：The verification step that exercises the behavior being checked.
- `observation: observation`：The tool result containing the expected output, content, or state.

成立条件：

- The action deliberately exercises the configured behavior to verify it, such as retrieving served content, performing a login, or querying the live state.
- The observation contains the specific expected value, content, or success marker, not merely a generic exit status, that demonstrates the verified behavior.

排除条件：

- The observation reports an error or an unexpected value.
- The observation reports only generic execution success without evidence of the expected behavior.
- The action only writes configuration, starts a service, or checks syntax without exercising the behavior.

### EXPLAINS_OBSERVED_ANOMALY

签名：`EXPLAINS_OBSERVED_ANOMALY(explanation: reasoning, anomalous_observation: observation)`

The reasoning gives a causal account of why a recorded observation returned an unexpected, empty, or otherwise puzzling result that is not itself an error, naming a concrete mechanism (tool or option semantics, symlink handling, process lifecycle) rather than treating the result as a failure of the underlying goal.

参数：

- `explanation: reasoning`：The agent text that accounts for the puzzling result.
- `anomalous_observation: observation`：The observation whose output was empty, missing, or contrary to expectation without reporting an error.

成立条件：

- The explanation explicitly refers to a result contained in the observation that deviated from expectation or left a property undetermined.
- The explanation identifies a concrete cause for that result, such as a command that does not follow symlinks, a shell lacking a numeric conversion function, or a non-reaping parent process.

排除条件：

- The reasoning merely restates or quotes the observation without a causal account.
- The reasoning only proposes the next action and gives no cause for the puzzling result.
- The referenced result is not present in the observation, so there is no traceable link between the two nodes.
- The observation reports a tool error or failing command; causal explanation of an error is a failure-diagnosis mechanism rather than an anomaly explanation.

### REVERIFIES_WITH_ALTERNATIVE_MECHANISM

签名：`REVERIFIES_WITH_ALTERNATIVE_MECHANISM(recheck_action: action, inconclusive_observation: observation)`

A prior observation left a system property undetermined or contradicted expectation without reporting an error, and the action re-establishes that same property through a different tool, option, or access path rather than repeating the original check.

参数：

- `recheck_action: action`：The action performing the alternative re-verification.
- `inconclusive_observation: observation`：The earlier check whose output was empty, ambiguous, or insufficient to settle the property.

成立条件：

- The prior observation failed to reveal a property that the agent expected or needed to know, for example because it produced no output.
- The action inspects the same system property using a different command, option, or access path than the earlier check.
- The differing technique is what makes the property observable.

排除条件：

- The action reruns the identical command with identical options, adding no new observability.
- The action inspects a different property than the one left undetermined.
- The earlier observation was conclusive, so the action is routine verification rather than alternative re-verification.
- The earlier observation reported a tool error; correcting a failed invocation is a distinct mechanism.

### RESOLVES_FUNCTIONAL_DOUBT_BY_PROBE

签名：`RESOLVES_FUNCTIONAL_DOUBT_BY_PROBE(doubt_reasoning: reasoning, probe_action: action, probe_result: observation)`

The reasoning raises doubt about whether an observed anomaly actually impairs a required capability, a probe action exercises exactly that capability, and the resulting observation demonstrates that the capability still works, providing grounds to dismiss the anomaly.

参数：

- `doubt_reasoning: reasoning`：The agent text expressing uncertainty about whether the anomaly breaks functionality.
- `probe_action: action`：The action that exercises the capability put in doubt.
- `probe_result: observation`：The observation reporting the outcome of the probe.

成立条件：

- The reasoning identifies an observed anomaly and questions whether it affects a required capability.
- The probe action directly exercises the capability that was questioned.
- The probe result shows the capability behaving successfully, providing grounds to treat the anomaly as harmless.

排除条件：

- The probe does not target the capability that was questioned.
- The probe result is failing, inconclusive, or unrelated to the doubt.
- No doubt about functionality is expressed; the probe is ordinary acceptance testing.

### VERIFIES_ENUMERATED_STATE_ITEMS

签名：`VERIFIES_ENUMERATED_STATE_ITEMS(checklist_reasoning: reasoning, inspection_action: action)`

The reasoning itemizes discrete facets of system state to be confirmed, and the action performs a read-only inspection that reads back those same facets in one pass.

参数：

- `checklist_reasoning: reasoning`：The agent text enumerating the specific facets to be confirmed.
- `inspection_action: action`：The read-only action that reads back the enumerated state facets.

成立条件：

- The reasoning lists multiple discrete facets to confirm, such as services, listening ports, ownership or permissions, repository references, configuration contents, and endpoint status.
- The action issues read-only commands covering those same facets.
- The facets checked by the action can be mapped onto the enumerated items.

排除条件：

- The action mutates state rather than reading it back.
- The action checks facets that were not enumerated, or the reasoning gives only a general goal without itemized facets.
- The reasoning enumerates items but the action addresses only one of them.

### PROVISIONS_DISPOSABLE_CREDENTIAL

签名：`PROVISIONS_DISPOSABLE_CREDENTIAL(provisioning_action: action)`

The action creates transient authentication material in a temporary location and installs it into the authentication path solely so that the login or authentication flow can be exercised during testing, without intending it as the end user's credential.

参数：

- `provisioning_action: action`：The action generating and installing the temporary credential.

成立条件：

- The action generates authentication material such as a key pair or token at a temporary path.
- The generated material is placed into the authentication path, such as an authorized-keys file, so that a test login can succeed.
- The material is distinct from the credential the end user is expected to configure.

排除条件：

- The action sets up the credential the end user will keep and use.
- The action only reads or inspects existing credentials without generating new material.
- Generated material is intended for permanent production use rather than a test of the authentication path.

### REPLICATES_DOCUMENTED_USER_COMMANDS

签名：`REPLICATES_DOCUMENTED_USER_COMMANDS(sequence_reasoning: reasoning, replay_action: action)`

The reasoning lays out the exact command sequence the requester is expected to run, and the action executes that same sequence verbatim against the configured system in a fresh working location as an acceptance replay of the requester's workflow.

参数：

- `sequence_reasoning: reasoning`：The agent text enumerating the expected command sequence.
- `replay_action: action`：The action executing the documented command sequence.

成立条件：

- The reasoning enumerates the specific commands the requester will run, in order.
- The action executes those same commands, in the same order, rather than ad-hoc equivalents.
- The execution occurs in a clean location so the result reflects the requester's starting conditions.

排除条件：

- The action uses substitute commands that only approximate the documented workflow.
- The reasoning states general verification goals without listing a concrete command sequence.
- The action executes only a fragment of the documented sequence.

### INSTALLS_STARTUP_HOOK

签名：`INSTALLS_STARTUP_HOOK(hook_action: action)`

The action modifies shell startup configuration so that a previously created helper is invoked automatically on future login or interactive shells, wiring the helper into the session lifecycle.

参数：

- `hook_action: action`：The action writing or appending the helper invocation into startup files.

成立条件：

- The action writes to shell startup configuration, such as a profile directory file or a shell rc file.
- The written content invokes a named helper, for example by its script path, so that it runs on subsequent shells.
- The invocation is written in a failure-tolerant form that does not disturb the session.

排除条件：

- The action only creates the helper file without wiring it into startup configuration.
- The startup file is edited for unrelated purposes such as environment variables, aliases, or PATH, with no helper invocation.
- The invocation is written into a one-off command rather than persistent startup configuration.

### REUSES_ARTIFACT_CREATED_BY_EARLIER_ACTION

签名：`REUSES_ARTIFACT_CREATED_BY_EARLIER_ACTION(consumer_action: action, producer_action: action)`

An artifact such as a file, script, credential, or directory produced by one action is consumed as an operational input by a later action, creating a traceable cross-action dependency on that produced value.

参数：

- `consumer_action: action`：The later action whose command references the produced artifact.
- `producer_action: action`：The earlier action that created the artifact.

成立条件：

- The producer action creates a file, script, credential, or path at a specific location.
- The consumer action's command references that same location as an operational input, for example as a key path or a generated script path.
- The producer precedes the consumer, and no other node supplies the artifact.

排除条件：

- Both actions merely reference an artifact that pre-existed and was not created by the producer.
- The consumer action mentions the path only in narration without using it operationally.
- The artifact was created by an action outside the compared pair.

### CONFIRMS_DEPLOYMENT_PIPELINE

签名：`CONFIRMS_DEPLOYMENT_PIPELINE(publish_action: action, retrieval_action: action, served_result: observation)`

A publishing action successfully writes content into the configured deployment source, and a subsequent retrieval action reads that content back through the serving endpoint, with the result showing that the published content is actually being served.

参数：

- `publish_action: action`：The action that commits, pushes, or installs content into the repository or deployment source.
- `retrieval_action: action`：The action that fetches the content through the serving endpoint.
- `served_result: observation`：The observation reporting the retrieved content and the server response.

成立条件：

- The publishing action reports success in writing the content to the deployment source.
- The retrieval action addresses the serving endpoint that is supposed to expose that content after deployment.
- The served result contains the published content with a success status, showing that the publish-to-serve path works end to end.

排除条件：

- The retrieval occurs before the publishing action succeeds, so the served result cannot stem from that deployment.
- The served content differs from what was published.
- The retrieval reads a local copy or the repository directly rather than the serving endpoint.

### DETECTS_SOURCE_CONTENT_MISMATCH

签名：`DETECTS_SOURCE_CONTENT_MISMATCH(reasoning: reasoning)`

The reasoning identifies that the content returned from a data source does not correspond to that source's declared or expected identity, by comparing source-level labels with identifiers or structure present in the returned content.

参数：

- `reasoning: reasoning`：The agent text identifying the mismatch between the declared source identity and the returned content.

成立条件：

- The reasoning compares a source's declared label, such as its file name or requested identity, with identifiers or structure present in the returned content.
- The reasoning states that the content actually corresponds to a different identity than the declared source.

排除条件：

- The reasoning only parses or summarizes the returned content without claiming an identity mismatch.
- The discrepancy is incidental formatting rather than a conflict between declared and observed source identity.
- The reasoning merely reports that a tool call returned an error.

### RESOLVES_SOURCE_IDENTITY_AMBIGUITY

签名：`RESOLVES_SOURCE_IDENTITY_AMBIGUITY(reasoning: reasoning)`

The reasoning addresses conflicting or ambiguous source identities by considering the plausible mappings of the supplied data and adopting an interpretation whose conclusions hold under all of them, instead of committing to a single unverified mapping.

参数：

- `reasoning: reasoning`：The agent text resolving the ambiguity in source identity or data mapping.

成立条件：

- The reasoning makes the ambiguity explicit by considering at least two plausible mappings or interpretations of the supplied data.
- The reasoning adopts an interpretation or course of action whose result is invariant across those mappings, so the ambiguity no longer affects the task outcome.

排除条件：

- The reasoning selects one mapping without considering alternatives.
- The reasoning notes the ambiguity but takes no position that resolves it for the task.
- The reasoning merely restates the identity mismatch without drawing any consequence for how to proceed.

### DERIVES_SOLUTION_FROM_OBSERVED_DATA

签名：`DERIVES_SOLUTION_FROM_OBSERVED_DATA(reasoning: reasoning, observations: observation[])`

The reasoning derives a candidate solution by extracting structured data from the payloads of observations and combining those extracted values in a computation or selection.

参数：

- `reasoning: reasoning`：The reasoning that analyzes the observation payloads and derives the candidate solution.
- `observations: observation[]`：The observations whose returned payloads are jointly analyzed to derive the candidate solution.

成立条件：

- The reasoning extracts specific values, records, events, or constraints from the content returned by the observations.
- The candidate solution depends on the collective payload content of the observations rather than on their success status alone.
- The reasoning computes or selects the candidate solution from those extracted values.

排除条件：

- The observations are used only to confirm that an action succeeded.
- The candidate solution is stated without using the observation payload data as operational input.
- The reasoning only draws a general environment constraint from a single observation rather than deriving a solution.

### PROPOSES_CONCRETE_SOLUTION

签名：`PROPOSES_CONCRETE_SOLUTION(reasoning: reasoning)`

The reasoning states a specific, directly implementable solution or selection, such as a concrete value, configuration, or chosen item, rather than only describing requirements, criteria, or a search process.

参数：

- `reasoning: reasoning`：The agent text proposing the concrete solution or selection.

成立条件：

- The reasoning identifies at least one concrete value, item, configuration, or outcome that constitutes the selected solution.
- The stated specificity is sufficient to implement or verify the solution directly.

排除条件：

- The reasoning only enumerates requirements, constraints, or candidate approaches without selecting one.
- The reasoning only restates a solution that was already implemented or observed rather than proposing it.

### IMPLEMENTS_SELECTED_SOLUTION

签名：`IMPLEMENTS_SELECTED_SOLUTION(solution_action: action, reasoning: reasoning)`

The action produces the task's deliverable artifact, and that artifact embodies the concrete solution previously selected in the reasoning.

参数：

- `solution_action: action`：The action that creates or modifies the deliverable artifact.
- `reasoning: reasoning`：The reasoning that selected the concrete solution.

成立条件：

- The reasoning states a concrete selected solution before the action.
- The artifact written or modified by the action contains the key values, structure, or decision of that selected solution.
- The artifact is the task's deliverable rather than auxiliary tooling, a test, or a diagnostic.

排除条件：

- The action creates a script, test, or diagnostic tool instead of the deliverable artifact.
- The reasoning contains only a general plan or multiple unselected options.
- The content of the action cannot be traced to the selected solution.

### CREATES_VERIFICATION_ARTIFACT

签名：`CREATES_VERIFICATION_ARTIFACT(verification_action: action, reasoning: reasoning)`

The action writes or rewrites a programmable artifact whose purpose is to automatically check another artifact or result against conditions specified in the reasoning.

参数：

- `verification_action: action`：The action creating or rewriting the verification artifact.
- `reasoning: reasoning`：The reasoning specifying the checks or validation procedure to be encoded.

成立条件：

- The reasoning specifies checks or validation steps to be performed.
- The action writes a script, test, or equivalent programmable artifact containing those checks.
- The verification artifact is separate from the solution artifact it inspects.

排除条件：

- The action creates the task's deliverable artifact rather than a verification tool.
- The action only runs an already existing check without creating or rewriting it.
- The reasoning only states that verification should happen without defining any check content.

### REPORTS_EXECUTION_FAILURE

签名：`REPORTS_EXECUTION_FAILURE(observation: observation)`

The observation indicates that an executed action or script did not complete successfully and supplies diagnostic evidence of the failure.

参数：

- `observation: observation`：The observation reporting failed execution or diagnostic error output.

成立条件：

- The observation is marked as an error or contains explicit failure output such as a traceback, error message, or failure summary.
- The failure concerns the execution of the invoked operation itself.

排除条件：

- The observation reports successful completion or normal output.
- The observation contains only a warning or an expected negative result.
- The observation reports an empty or unsuccessful search result that is a legitimate outcome of the operation rather than an execution failure.

### CONFIRMS_VERIFICATION_SUCCESS

签名：`CONFIRMS_VERIFICATION_SUCCESS(observation: observation)`

The observation reports that a validation procedure completed and that the conditions it was meant to check were satisfied.

参数：

- `observation: observation`：The observation reporting the successful validation result.

成立条件：

- The observation contains an explicit success statement or passing verdict for the validation.
- The reported result covers the conditions the validation was designed to check, not a single incidental assertion.

排除条件：

- The observation returns raw data, file contents, or a listing without any validation verdict.
- The observation reports a failing or only partially passing validation.

### PERFORMS_INTEGRITY_CHECK

签名：`PERFORMS_INTEGRITY_CHECK(action: action)`

The action inspects checksums, hashes, or modification metadata of named resources in order to establish whether protected inputs have remained unchanged.

参数：

- `action: action`：The action performing the integrity check.

成立条件：

- The action computes or retrieves checksums, hashes, sizes, or modification timestamps for named resources.
- The check is directed at confirming that those resources were not modified.

排除条件：

- The action merely reads or writes the content of the resources without inspecting integrity metadata.
- The action lists files for a purpose other than confirming that protected inputs are unchanged.

### PROVIDES_INTEGRITY_EVIDENCE

签名：`PROVIDES_INTEGRITY_EVIDENCE(observation: observation)`

The observation returns checksums, hashes, or comparable metadata for named resources that allows their modification state to be assessed.

参数：

- `observation: observation`：The observation providing integrity-relevant metadata for named resources.

成立条件：

- The observation contains integrity-relevant metadata such as checksums, hashes, sizes, or modification timestamps for named resources.
- The metadata is tied to specific named resources whose integrity is at issue.

排除条件：

- The observation contains only file contents, execution output, or success messages.
- The observation provides a bare directory listing with no integrity-relevant metadata.
