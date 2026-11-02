# 第 1 批 Predicate Discovery 结果

## 一、批次信息

处理 Window：1–5
Prompt 版本：v0001
本批新增谓词：40
本批已有谓词修订：2
当前谓词总数：40

## 二、本批新增谓词

### IS_PLAN

签名：`IS_PLAN(reasoning: reasoning)`

The reasoning explicitly expresses an intended future action or sequence of actions that the agent intends to carry out next.

参数：

- `reasoning: reasoning`：The agent text expressing the intended future action or sequence of actions.

成立条件：

- The reasoning identifies at least one action to be performed later, such as inspecting a file, writing content, compiling, or verifying output.
- The intended action is stated prospectively rather than reported as already done.

排除条件：

- The reasoning only reports or summarizes actions already completed.
- The reasoning only restates file content or tool output without expressing an intended next action.

### DIAGNOSES_OBSERVED_FAILURE

签名：`DIAGNOSES_OBSERVED_FAILURE(reasoning: reasoning, failure: observation)`

The reasoning explains the cause of a failure reported by an observation and derives a corrective approach from that explanation.

参数：

- `reasoning: reasoning`：The agent text explaining why the observed failure occurred and what should change.
- `failure: observation`：The observation reporting the failure being explained.

成立条件：

- The observation indicates that an invoked operation did not succeed.
- The reasoning identifies a concrete cause for the failure and states a corrective approach or change based on that cause.

排除条件：

- The reasoning merely notes that something failed without offering a causal explanation.
- The reasoning explains an unrelated issue or offers no corrective direction.

### GUIDES_ACTION

签名：`GUIDES_ACTION(reasoning: reasoning, action: action)`

The action's tool choice, target, or argument values instantiate an intent, diagnosis, or corrected approach explicitly stated in the reasoning.

参数：

- `reasoning: reasoning`：The agent text stating the plan, diagnosis, or corrected approach.
- `action: action`：The action whose tool, target, or arguments carry out that stated approach.

成立条件：

- The reasoning specifies the operation or correction to perform, and the action performs that same operation with matching target or arguments.
- A traceable correspondence exists between the described step and the executed parameters, command, path, or content.

排除条件：

- The action is unrelated to the described step or diverges from it in target or approach.
- The reasoning only reports prior results and the action is merely temporally adjacent.

### USES_OBSERVATION_AS_INPUT

签名：`USES_OBSERVATION_AS_INPUT(action: action, observation: observation)`

The action uses an identifiable value or payload supplied by a prior observation as an operational input.

参数：

- `action: action`：The action receiving the input.
- `observation: observation`：The prior observation supplying the input value or payload.

成立条件：

- An argument, file content, path, or identifier of the action can be traced to content present in the observation.
- The observation precedes the action within the trajectory.

排除条件：

- The observation only guides action selection without supplying an operational input value.
- The nodes are merely temporally adjacent or topically related without a traceable value transfer.

### ATTEMPTS_REPAIR

签名：`ATTEMPTS_REPAIR(repair: action, failure: observation)`

The action modifies the command, parameters, or content that previously produced an observed failure in order to address that failure.

参数：

- `repair: action`：The action attempting to repair the failure.
- `failure: observation`：The earlier observation reporting the failure.

成立条件：

- The failure observation precedes the repair action and indicates that the operation did not succeed.
- The action preserves the original goal while changing the element identified as faulty, such as an option's argument form, a path, or source content.

排除条件：

- The action repeats the failing invocation without any change.
- The action pursues a different goal unrelated to the reported failure.
- No confirming evidence is required for this predicate; confirmation is a separate mechanism.

### CONFIRMS_REPAIR

签名：`CONFIRMS_REPAIR(repair: action, failure: observation, check_result: observation)`

A repair action addresses an observed failure, and a subsequent execution result confirms that the original failure has been resolved.

参数：

- `repair: action`：The action attempting to repair the failure.
- `failure: observation`：The earlier observation reporting the failure.
- `check_result: observation`：The later observation establishing that the original failure no longer occurs.

成立条件：

- The failure precedes the repair, and the repair changes the failing element.
- The later result shows the target operation or content being produced, loaded, or otherwise completed successfully, with no recurrence of the original error.

排除条件：

- The repair is attempted without any later result.
- The later output repeats the original error or otherwise fails to establish resolution.

### REPORTS_FAILURE

签名：`REPORTS_FAILURE(observation: observation)`

The observation indicates that the invoked operation did not succeed.

参数：

- `observation: observation`：The tool result being evaluated for failure.

成立条件：

- The observation carries an error indication, a non-success exit status, or an explicit error message such as a missing file or unloadable module.

排除条件：

- The observation reports successful completion or plain data output without any error indication.

### REPORTS_SUCCESS

签名：`REPORTS_SUCCESS(observation: observation)`

The observation indicates that the invoked operation completed successfully.

参数：

- `observation: observation`：The tool result being evaluated for success.

成立条件：

- The observation contains an explicit success message, a clean completion with no error indication, or a listing of the expected produced artifacts.

排除条件：

- The observation reports an error or non-success exit status.
- The output is only a partial or ambiguous progress message.

### IS_COMPLETION_CONCLUSION

签名：`IS_COMPLETION_CONCLUSION(reasoning: reasoning)`

The reasoning declares the overall objective achieved and cites the verification evidence that supports the claim.

参数：

- `reasoning: reasoning`：The agent text asserting task completion.

成立条件：

- The reasoning states that the requested objective has been fulfilled.
- It references concrete evidence obtained earlier, such as produced artifacts or verified output.

排除条件：

- The reasoning states plans or intermediate steps while work remains.
- The reasoning reports observations without concluding that the objective is achieved.

### IDENTIFIES_MISSING_SOFTWARE_DEPENDENCY

签名：`IDENTIFIES_MISSING_SOFTWARE_DEPENDENCY(reasoning: reasoning, observation: observation)`

The reasoning interprets an environment probe as showing that software required for the task is absent and treats obtaining that software as a prerequisite for proceeding with the intended configuration.

参数：

- `reasoning: reasoning`：The agent text diagnosing the environment and naming the missing capability.
- `observation: observation`：The probe result showing which required tools or services are absent.

成立条件：

- The observation reports probe results about the environment, such as available binaries, packages, or running processes, and shows that one or more task-required tools or services are unavailable.
- The reasoning explicitly connects that absence to the task and indicates that the missing software must be supplied before the intended work can proceed.

排除条件：

- The observation merely enumerates installed software or environment details without revealing a missing task requirement.
- The reasoning restates the task or lists actions without connecting an observed absence to a prerequisite that must be supplied.
- The reasoning explains a failed operation rather than an absent prerequisite.

### ADAPTS_TO_ABSENT_SERVICE_MANAGER

签名：`ADAPTS_TO_ABSENT_SERVICE_MANAGER(reasoning: reasoning, observation: observation)`

The reasoning infers from a process or runtime observation that no conventional service manager or init system is available, and consequently adopts direct or manual control of services instead of the usual management mechanism.

参数：

- `reasoning: reasoning`：The agent text inferring the absence of an init or service manager and adapting the startup strategy.
- `observation: observation`：The process or runtime listing showing that the environment lacks a conventional service manager.

成立条件：

- The observation exposes process or runtime state showing that the environment is not controlled by a conventional init or service manager.
- The reasoning explicitly concludes that services cannot be managed through that absent mechanism and selects direct daemon startup, manual supervision, or an equivalent non-init strategy.

排除条件：

- The observation does not expose process or runtime state relevant to how services are managed.
- The reasoning plans service startup without noting that a management mechanism is absent.
- A service manager is present and the reasoning uses it in the usual way.

### PREPARES_ACCOUNT_FOR_KEY_AUTHENTICATION

签名：`PREPARES_ACCOUNT_FOR_KEY_AUTHENTICATION(action: action)`

The action configures a service account with a usable login environment and a non-locking authentication state, together with key-access ownership and permissions, so the account can be reached remotely without password login and can own the service's data.

参数：

- `action: action`：The account-creation and authentication-state adjustment command or script.

成立条件：

- The action creates or selects an account with a usable login shell and home directory.
- The action places the account's authentication state in a non-locking form so that key-based login is not rejected.
- The action creates a user-owned .ssh directory with restrictive permissions and an authorized-keys file ready to receive public keys.

排除条件：

- The action creates an account but leaves it locked or otherwise unable to accept key-based login.
- The action adjusts unrelated account attributes without preparing remote key-based access.

### INITIALIZES_BARE_REPOSITORY

签名：`INITIALIZES_BARE_REPOSITORY(action: action)`

The action establishes a bare repository as a push target at the intended service location, points its default branch reference at the branch clients will push, and places it under ownership that allows the service account to receive pushes.

参数：

- `action: action`：The repository initialization, branch-reference, and ownership command.

成立条件：

- The action creates a bare repository at the intended service path.
- The action sets HEAD or an equivalent symbolic reference to the designated default branch.
- The action assigns repository ownership or equivalent write authority to the service account.

排除条件：

- The action initializes a non-bare working repository rather than a push target.
- The repository is left without the intended default branch or without ownership permitting the service account to receive pushes.

### CONFIGURES_PUSH_TRIGGERED_DEPLOYMENT

签名：`CONFIGURES_PUSH_TRIGGERED_DEPLOYMENT(action: action)`

The action installs an executable repository hook that reacts to pushed branch references by deploying the pushed content into the directory served by the web server.

参数：

- `action: action`：The hook-writing or hook-installation action.

成立条件：

- The action writes an executable hook into the repository's hook directory.
- The hook logic reads pushed references and performs a work-tree checkout or equivalent deployment into the served document root.
- The hook limits deployment to branch updates and excludes non-branch or branch-deletion events.

排除条件：

- The hook only logs, notifies, or performs an action unrelated to deploying pushed content.
- Deployment into the served directory is not part of the hook behavior.

### CONFIGURES_SERVICE_ENDPOINT

签名：`CONFIGURES_SERVICE_ENDPOINT(action: action)`

The action writes or replaces the active configuration of a network service so that the service listens on the task-required port and serves content from the intended document root.

参数：

- `action: action`：The configuration-writing action that defines the service endpoint.

成立条件：

- The configuration specifies the task-required listen port.
- The configuration specifies the document root from which content should be served.
- The configuration is written to an active configuration location or to one that the service loads.

排除条件：

- The action edits an inactive or sample configuration that the service does not load.
- The action changes unrelated directives without defining the required port and document root.

### PREPARES_DEPLOYMENT_DIRECTORY

签名：`PREPARES_DEPLOYMENT_DIRECTORY(action: action)`

The action prepares the directory served by the web server so that the deployment account can write pushed content into it while the server process retains read access to that content.

参数：

- `action: action`：The directory-creation and ownership or permission adjustment command.

成立条件：

- The action creates the served directory or confirms that it exists.
- The action assigns ownership or permissions that allow the deployment account to write into the directory.
- The resulting ownership and permissions leave the content readable by the web server process.

排除条件：

- The action only reads or lists the directory without preparing it for deployment.
- The action changes ownership or permissions in a way that prevents the web server process from reading deployed content.

### VALIDATES_AND_ENABLES_SERVICE_CONFIGURATION

签名：`VALIDATES_AND_ENABLES_SERVICE_CONFIGURATION(action: action)`

The action confirms that the intended service configuration is enabled and syntactically valid, and makes service startup conditional on that confirmation succeeding.

参数：

- `action: action`：The validation and activation command sequence.

成立条件：

- The action checks whether the intended configuration is enabled or linked into the active configuration set.
- The action runs a syntax or consistency check on the service configuration.
- Startup of the service is chained to the success of the check.

排除条件：

- The service is started without any configuration validation.
- A validation command is run but its failure does not prevent startup.

### STARTS_SERVICE_DAEMONS_DIRECTLY

签名：`STARTS_SERVICE_DAEMONS_DIRECTLY(action: action)`

The action launches the required long-running service daemons directly rather than through a service manager, preparing any runtime prerequisites those daemons need in order to start and remain running.

参数：

- `action: action`：The daemon-launching command or script.

成立条件：

- The action invokes daemon binaries or equivalent direct start commands for the required network services.
- The action prepares runtime prerequisites such as directories, host keys, or runtime state needed for those daemons to start.
- The launched processes are intended to remain running after the invoking command returns.

排除条件：

- The action only installs packages without launching the services.
- The action delegates startup to a service manager or init system.
- The action starts only a transient foreground process instead of the required long-running daemon.

### ESTABLISHES_LOCAL_HOSTNAME_RESOLUTION

签名：`ESTABLISHES_LOCAL_HOSTNAME_RESOLUTION(action: action)`

The action adds a local name-resolution mapping so that the hostname used in the task's client commands resolves to the local or container-reachable address of the service.

参数：

- `action: action`：The hostname or resolver configuration action.

成立条件：

- The action adds or modifies a local hosts-file or equivalent resolver entry.
- The entry maps the task's service hostname to an address that reaches the local service.

排除条件：

- The action changes the machine's own hostname rather than adding a service-name mapping.
- The action only relies on external name resolution without adding the local mapping.

### GUIDES_CONFIGURATION_CHANGE

签名：`GUIDES_CONFIGURATION_CHANGE(observation: observation, action: action)`

An observation exposes the current structure or values of a service configuration, and a subsequent action rewrites that same configuration to the task-required values, using the observed structure to locate or shape the change.

参数：

- `observation: observation`：The observation revealing existing configuration values or activation structure.
- `action: action`：The later action that rewrites the observed configuration.

成立条件：

- The observation shows current configuration details such as a listen directive, a document root, or the active-configuration linkage.
- A subsequent action writes or replaces that same configuration, changing the identified values to the task-required values.
- The correspondence between the observed configuration and the rewritten configuration is identifiable as the same file or the same service configuration.

排除条件：

- The observation supplies an operational data value rather than configuration structure or values.
- The subsequent action modifies an unrelated configuration without using the observed structure or values.
- The action writes a configuration without any prior inspection of that configuration.

### PLANS_END_TO_END_VERIFICATION

签名：`PLANS_END_TO_END_VERIFICATION(reasoning: reasoning)`

The reasoning lays out a forthcoming verification procedure that reproduces the requester's prescribed end-user workflow against the configured system, and identifies the observable outcome by which the procedure's success will be judged.

参数：

- `reasoning: reasoning`：The agent text that specifies the forthcoming validation procedure and its expected outcome.

成立条件：

- The reasoning names at least one end-user interaction from the request, such as authenticating, cloning, committing, pushing, or retrieving the deployed path, as something to be executed for validation.
- The reasoning identifies the observable result that the procedure should produce, so that success can be judged.

排除条件：

- The reasoning only describes configuration changes or service management to be performed.
- The reasoning only reports results of checks already completed, without specifying a forthcoming verification procedure.
- The reasoning plans only an internal or intermediate check that does not exercise the requester's end-user interaction.

### EXECUTES_USER_WORKFLOW_TRIAL

签名：`EXECUTES_USER_WORKFLOW_TRIAL(action: action)`

The action runs the requester's prescribed end-user command sequence, or a faithful stand-in for it, against the configured system as a functional acceptance trial of the delivered capability rather than as configuration or state inspection.

参数：

- `action: action`：The tool invocation that exercises the user-facing flow end to end.

成立条件：

- The invocation contains commands reproducing the end-user interaction from the request, such as a remote clone followed by commit and push, or a retrieval of the deployed path.
- The invocation occurs after the relevant configuration has been applied, so that its result reflects the delivered capability.

排除条件：

- The invocation only edits configuration files, starts services, or inspects filesystem or process state.
- The invocation exercises only an internal component rather than the requester-visible flow.
- The invocation merely prepares or cleans up the trial environment without exercising the user-facing flow.

### OBSERVATION_CONFIRMS_REQUESTED_BEHAVIOR

签名：`OBSERVATION_CONFIRMS_REQUESTED_BEHAVIOR(observation: observation)`

The observation carries the outcome of a user-facing interaction whose content matches the end-user-visible behavior specified in the request, providing direct evidence that the delivered system produces the requested result.

参数：

- `observation: observation`：The tool result carrying the outcome of the user-facing interaction.

成立条件：

- The output contains the result the requester stated they expect, such as served content equal to the specified payload or the expected response from the retrieved resource.
- The result is returned without an error status or failure indication.

排除条件：

- The output shows only configuration, process, or filesystem state.
- The output differs from the requested result, is empty, or reports an error or missing resource.

### OBSERVATION_CONFIRMS_SERVICE_AVAILABILITY

签名：`OBSERVATION_CONFIRMS_SERVICE_AVAILABILITY(observation: observation)`

The observation provides evidence that the required long-running services are active and reachable, through live process entries or through listening-socket entries for the required ports.

参数：

- `observation: observation`：The tool result listing running processes or listening sockets.

成立条件：

- The output shows running process instances for the required daemons, or sockets in the listening state for the required ports.
- The evidence is produced without error markers or missing entries for the required services.

排除条件：

- The output is only a configuration syntax validation or a confirmation that a file was written or edited.
- The output names the services but gives no indication that processes are running or ports are listening.

### ATTRIBUTES_FAILURE_TO_TRIAL_SETUP

签名：`ATTRIBUTES_FAILURE_TO_TRIAL_SETUP(reasoning: reasoning, observation: observation)`

The reasoning concludes that an observed failure originates in the agent's own trial setup or command construction rather than in the delivered system, so no change to the delivered configuration is required.

参数：

- `reasoning: reasoning`：The agent text classifying the origin of the failure.
- `observation: observation`：The tool result reporting the failure whose origin is being classified.

成立条件：

- The reasoning explicitly links the failure to a characteristic of the trial environment or of how the trial command was assembled.
- The reasoning states that the delivered system itself remains correct, or that the failure would not occur for the requester.

排除条件：

- The reasoning treats the failure as a defect of the delivered system.
- The reasoning does not distinguish trial-induced failure from genuine system failure.

### JUDGES_OBSERVATION_CONCLUSIVENESS

签名：`JUDGES_OBSERVATION_CONCLUSIVENESS(reasoning: reasoning, observation: observation)`

The reasoning assesses whether an indirect, low-detail, or empty observation is sufficient to establish the intended property, drawing on auxiliary cues such as reported size, known content, structural knowledge, or tool behavior.

参数：

- `reasoning: reasoning`：The agent text assessing the evidential value of the observation.
- `observation: observation`：The low-detail, empty, or indirect tool result being assessed.

成立条件：

- The reasoning explains why the observation's content, or its absence of output, does or does not establish the target property.
- When the evidence is judged insufficient, the reasoning states what alternative evidence or check is required.

排除条件：

- The reasoning accepts the observation's output at face value without evaluating its sufficiency.
- The reasoning addresses a different observation than the one being judged.

### DELEGATES_OPERATION_TO_RESOURCE_OWNER

签名：`DELEGATES_OPERATION_TO_RESOURCE_OWNER(action: action, rejection: observation)`

In response to a reported ownership or permission refusal, the action performs the rejected operation under the identity that owns the resource instead of the rejected identity.

参数：

- `action: action`：The invocation that re-executes the operation under the owning identity.
- `rejection: observation`：The earlier tool result reporting the ownership or permission error.

成立条件：

- The earlier observation contains an ownership or permission refusal that names the resource.
- The action switches the executing identity to the owning account while preserving the operation's target and intent.

排除条件：

- The earlier error concerns connectivity, availability, or a missing file rather than ownership or permission.
- The action resolves the refusal by changing the resource's ownership or permissions instead of changing the executing identity.
- The action continues to run under the rejected identity.

### CLEANS_TEST_ARTIFACTS

签名：`CLEANS_TEST_ARTIFACTS(action: action)`

The action removes or reverts state created during the agent's own trials — temporary credentials, cloned working copies, trial commits and pushed references, and files deployed by the trials — so the delivered system returns to its pre-trial state.

参数：

- `action: action`：The cleanup invocation removing trial-created state.

成立条件：

- The invocation deletes or resets entities that the trials created, such as temporary keys, test clones, test commits or branch references, and files deployed by the trials.
- The invocation restores the initial structural state of the affected locations.

排除条件：

- The invocation only performs routine configuration or service management.
- The invocation deletes resources that belong to the delivered system rather than to the trials.
- The invocation only inspects state without modifying it.

### PRESERVES_USER_COMMAND_PRECONDITIONS

签名：`PRESERVES_USER_COMMAND_PRECONDITIONS(reasoning: reasoning)`

The reasoning identifies residual state that would cause the requester's own prescribed commands to fail or misbehave, and concludes that this state must be removed or reverted before handoff.

参数：

- `reasoning: reasoning`：The agent text linking leftover state to a concrete failure in the requester's command sequence.

成立条件：

- The reasoning identifies a specific leftover artifact, such as an already-existing commit or an already-deployed file.
- The reasoning names the concrete command from the request that would fail or misbehave because of that artifact, and calls for reverting it.

排除条件：

- The reasoning argues only for general tidiness without naming a command that would fail.
- The reasoning concludes that the leftover state is harmless for the requester's commands.

### JUSTIFIES_PREPARED_HANDOFF_STATE

签名：`JUSTIFIES_PREPARED_HANDOFF_STATE(reasoning: reasoning)`

The reasoning justifies deliberately leaving a pre-created but empty or inert artifact in place, rather than deleting or pre-populating it, because keeping it lets the requester's own subsequent manual step succeed without extra work.

参数：

- `reasoning: reasoning`：The agent text weighing removal against retention of a prepared artifact.

成立条件：

- The reasoning compares removing the prepared artifact with keeping it in an empty or inert form.
- The reasoning concludes that keeping it lets the requester's own setup step succeed without extra work.

排除条件：

- The reasoning only plans removal of the artifact.
- The reasoning pre-populates functional data that the requester is supposed to supply themselves.

### DERIVES_STATE_FROM_RAW_OUTPUT

签名：`DERIVES_STATE_FROM_RAW_OUTPUT(reasoning: reasoning, observation: observation)`

The reasoning translates low-level, encoded, or procedural output in the observation into an explicit semantic conclusion about the state of the system.

参数：

- `reasoning: reasoning`：The agent text that decodes the raw output into a stated system state.
- `observation: observation`：The tool result containing encoded, numeric, or procedural output such as hexadecimal socket entries and state codes, ref listings, or transfer logs.

成立条件：

- The observation contains tokens that are not directly human-meaningful, such as hexadecimal socket addresses and state codes, encoded status fields, ref listings, or version-control transfer transcripts.
- The reasoning explicitly maps those tokens to named system states, for example which ports are listening, which interfaces the services are bound to, or that a pushed branch was published.
- The stated conclusion is presented as the meaning of the observed output rather than as an independent guess.

排除条件：

- The observation already states a plain semantic conclusion that the reasoning only repeats.
- The reasoning quotes the output without assigning it a system-state meaning.
- The reasoning speculates about system state without grounding the conclusion in the observed tokens.
- The reasoning evaluates whether the observation is sufficient evidence rather than decoding its content.

### INSTALLS_STARTUP_HOOK_FOR_ARTIFACT

签名：`INSTALLS_STARTUP_HOOK_FOR_ARTIFACT(registration_action: action, creation_action: action)`

The later action registers an artifact created by an earlier action in shell, session, or system startup configuration so that the artifact is invoked automatically in future contexts, without altering the artifact's own content.

参数：

- `registration_action: action`：The action that writes or appends startup or session-initialization configuration referencing the artifact.
- `creation_action: action`：The earlier action that created the artifact being registered.

成立条件：

- The creation action produced a named executable, script, or configuration artifact whose creation is evidenced by its result.
- The registration action adds references to that artifact path in one or more startup or session-initialization files, such as a shell rc file, a profile drop-in, or an equivalent.
- The registration action leaves the artifact's content unchanged and only controls when or whether it is invoked.

排除条件：

- The artifact registered was not created by the earlier action in the same trajectory.
- The later action modifies or rewrites the artifact itself instead of registering it.
- The registration only applies an ownership or permission change without arranging automatic invocation.
- The two actions are only temporally adjacent and operationally unrelated.

### EXPLAINS_ANOMALY_AS_HARMLESS

签名：`EXPLAINS_ANOMALY_AS_HARMLESS(reasoning: reasoning, observation: observation)`

The reasoning investigates an anomalous condition visible in the observation, identifies its cause, and concludes that the anomaly does not affect the required functionality, relying on functional evidence rather than altering the configuration.

参数：

- `reasoning: reasoning`：The agent text that diagnoses and judges the anomalous condition.
- `observation: observation`：The tool result exhibiting the anomalous condition.

成立条件：

- The observation shows a condition that deviates from a clean expected state, such as lingering defunct processes, unexpected extra or missing entries, or an unexpectedly empty result.
- The reasoning offers a causal explanation for the anomaly that places its origin outside the delivered functionality.
- The reasoning concludes that the anomaly is cosmetic or non-impacting, citing evidence that the required functionality still succeeds, such as a fresh successful operation or a previously verified user-visible result.

排除条件：

- The anomaly is observed but not explained.
- The anomaly prompts a repair or configuration change.
- The reasoning asserts the condition is harmless without any causal account or functional evidence.
- The reasoning treats the anomaly as a defect of the delivered system.

### RESOLVES_DATA_INCONSISTENCY

签名：`RESOLVES_DATA_INCONSISTENCY(reasoning: reasoning)`

The reasoning detects a discrepancy or conflict among observed data — such as an unexpected mismatch between a container's label and the identifiers or attributes embedded in it — and resolves it by deciding how that data should be interpreted for the task.

参数：

- `reasoning: reasoning`：The agent text detecting the discrepancy and deciding how to interpret the data.

成立条件：

- The reasoning identifies a concrete conflict or unexpected mismatch in the observed data, for example between file names and the identifiers, labels, or attributes found inside them.
- The reasoning weighs the competing interpretations and adopts a decision about which interpretation to use, or concludes that the discrepancy does not affect the task.

排除条件：

- The reasoning merely quotes, summarizes, or reformats the observed data without noticing a discrepancy.
- A discrepancy is noted but its interpretation is left unresolved.
- The observed differences are ordinary expected variation rather than a conflict that requires interpretation.

### DERIVES_CONSTRAINED_SOLUTION

签名：`DERIVES_CONSTRAINED_SOLUTION(reasoning: reasoning)`

The reasoning derives a concrete solution by applying explicit constraints to candidate values, eliminating or comparing alternatives, and selecting a specific result.

参数：

- `reasoning: reasoning`：The agent text deriving the constrained solution.

成立条件：

- The reasoning applies stated constraints, limits, or preferences to candidate values.
- The reasoning compares alternatives or rules them out as infeasible.
- The reasoning states a specific selected solution, including any tie-breaker applied when several candidates remain.

排除条件：

- The reasoning only restates requirements or enumerates raw data.
- A candidate is proposed without being checked against the stated constraints.
- No concrete result is selected.

### GROUNDS_CONCLUSION_IN_OBSERVATION

签名：`GROUNDS_CONCLUSION_IN_OBSERVATION(reasoning: reasoning, observation: observation)`

The reasoning reaches a conclusion or makes a decision that relies on identifiable values, entries, or findings supplied by a prior observation.

参数：

- `reasoning: reasoning`：The reasoning that reaches the conclusion or decision.
- `observation: observation`：The prior observation supplying the substantive content used by the reasoning.

成立条件：

- A conclusion, decision, or derived value in the reasoning can be traced to specific substantive content of the observation.
- The observation precedes the reasoning and contributes data rather than only a success or failure indication.

排除条件：

- The observation only reports tool success or failure without substantive content used by the reasoning.
- The reasoning is only topically related to the observation and does not use its values.
- The conclusion is reached independently of the observation.

### GENERATES_DELIVERABLE_ARTIFACT

签名：`GENERATES_DELIVERABLE_ARTIFACT(action: action)`

The action writes a complete artifact to the task-designated output location, serving as the substantive deliverable of the task.

参数：

- `action: action`：The write action producing the deliverable artifact.

成立条件：

- The action is a write-type operation targeting the output location that the task designates for the deliverable.
- The written content is a complete artifact in the required format carrying the requested payload.

排除条件：

- The action writes an auxiliary script, temporary file, or partial snippet.
- The action reads rather than writes data.
- The action writes outside the designated deliverable location.

### AUTHORS_VALIDATION_PROGRAM

签名：`AUTHORS_VALIDATION_PROGRAM(action: action)`

The action creates or rewrites an executable program whose purpose is to check an artifact or solution against stated requirements and report pass/fail results.

参数：

- `action: action`：The write action authoring the validation program.

成立条件：

- The action writes executable code implementing validation logic.
- The program checks format, constraints, or correctness of an artifact or solution and emits an explicit pass/fail or error outcome.

排除条件：

- The action writes the data deliverable itself rather than a validator.
- The action runs an existing validator without authoring or rewriting its code.
- The action writes prose, data, or an incomplete snippet rather than an executable validation program.

### EXECUTES_VALIDATION_PROGRAM

签名：`EXECUTES_VALIDATION_PROGRAM(action: action)`

The action executes a program or script in order to check an artifact or solution against requirements and obtain verification evidence.

参数：

- `action: action`：The action executing the validation program.

成立条件：

- The tool invocation runs validation logic against an artifact or solution.
- The invocation's purpose is to assess correctness, and its result supplies pass/fail verification evidence.

排除条件：

- The action only reads, writes, or inspects the artifact without running validation logic.
- The action runs a command unrelated to assessing correctness.
- The action only authors validation code without executing it.

### CHECKS_INPUT_INTEGRITY

签名：`CHECKS_INPUT_INTEGRITY(action: action)`

The action performs read-only inspection of task input files' listing, metadata, or checksums in order to confirm that those inputs remain unmodified.

参数：

- `action: action`：The action inspecting the input files for integrity.

成立条件：

- The action inspects existing input files without altering them, for example by listing them with metadata or computing checksums.
- The inspection is aimed at confirming that the task inputs have not been modified.

排除条件：

- The action reads input content for task analysis rather than for verifying that inputs are unchanged.
- The action modifies or deletes input files.
- The action only checks the produced output artifact.

## 三、本批已有谓词修订

### ATTEMPTS_REPAIR → ATTEMPTS_REPAIR

Window：xhigh__configure-git-webserver__window_0002

修订前：

### ATTEMPTS_REPAIR

签名：`ATTEMPTS_REPAIR(repair: action, failure: observation)`

The action modifies the command, parameters, or content that previously produced an observed failure in order to address that failure.

参数：

- `repair: action`：The action attempting to repair the failure.
- `failure: observation`：The earlier observation reporting the failure.

成立条件：

- The failure observation precedes the repair action and indicates that the operation did not succeed.
- The action preserves the original goal while changing the element identified as faulty, such as an option's argument form, a path, or source content.

排除条件：

- The action repeats the failing invocation without any change.
- The action pursues a different goal unrelated to the reported failure.
- No confirming evidence is required for this predicate; confirmation is a separate mechanism.

修订后：

### ATTEMPTS_REPAIR

签名：`ATTEMPTS_REPAIR(repair: action, failure: observation)`

The action re-executes an operation whose prior result was inadequate — reporting an error or failing to produce the intended output — with the command, parameters, or environment changed so as to remove the identified cause.

参数：

- `repair: action`：The action attempting to repair the failure.
- `failure: observation`：The earlier observation reporting the failure or the unusable result.

成立条件：

- The failure observation precedes the repair action and indicates that the operation did not succeed or did not produce the intended result.
- The action preserves the original goal while changing the element identified as faulty, such as an option's argument form, the scope of an environment setting, a path, an executing identity, or source content.

排除条件：

- The action repeats the inadequate invocation without any change.
- The action pursues a different goal unrelated to the reported result.
- No confirming evidence is required for this predicate; confirmation is a separate mechanism.

### CLEANS_TEST_ARTIFACTS → CLEANS_TEST_ARTIFACTS

Window：xhigh__configure-git-webserver__window_0003

修订前：

### CLEANS_TEST_ARTIFACTS

签名：`CLEANS_TEST_ARTIFACTS(action: action)`

The action removes or reverts state created during the agent's own trials — temporary credentials, cloned working copies, trial commits and pushed references, and files deployed by the trials — so the delivered system returns to its pre-trial state.

参数：

- `action: action`：The cleanup invocation removing trial-created state.

成立条件：

- The invocation deletes or resets entities that the trials created, such as temporary keys, test clones, test commits or branch references, and files deployed by the trials.
- The invocation restores the initial structural state of the affected locations.

排除条件：

- The invocation only performs routine configuration or service management.
- The invocation deletes resources that belong to the delivered system rather than to the trials.
- The invocation only inspects state without modifying it.

修订后：

### CLEANS_TEST_ARTIFACTS

签名：`CLEANS_TEST_ARTIFACTS(action: action)`

The action removes or reverts state created during the agent's own trials — temporary credentials, cloned working copies, scratch directories, trial commits and pushed references, and files deployed by the trials — so the delivered system returns to the pristine state expected immediately before the requester's own first operation, while leaving the configured services and permanent infrastructure intact.

参数：

- `action: action`：The cleanup invocation removing trial-created state.

成立条件：

- The invocation deletes or resets entities that the trials created, such as temporary keys, test clones, scratch directories, test commits or branch references, and files deployed by the trials.
- The invocation restores the initial structural state of the affected locations, such as an empty reference set in the repository, an empty document root, or a credentials file ready to receive the requester's own key.
- The invocation leaves the configured services, account setup, and permanent configuration in place, so the requester's commands still succeed afterwards.

排除条件：

- The invocation only performs routine configuration or service management.
- The invocation deletes resources that belong to the delivered system rather than to the trials.
- The invocation only inspects state without modifying it.
- The reset is performed to repair a reported failure rather than to return the system to its pristine pre-trial state.

## 四、当前完整 Registry

### IS_PLAN

签名：`IS_PLAN(reasoning: reasoning)`

The reasoning explicitly expresses an intended future action or sequence of actions that the agent intends to carry out next.

参数：

- `reasoning: reasoning`：The agent text expressing the intended future action or sequence of actions.

成立条件：

- The reasoning identifies at least one action to be performed later, such as inspecting a file, writing content, compiling, or verifying output.
- The intended action is stated prospectively rather than reported as already done.

排除条件：

- The reasoning only reports or summarizes actions already completed.
- The reasoning only restates file content or tool output without expressing an intended next action.

### DIAGNOSES_OBSERVED_FAILURE

签名：`DIAGNOSES_OBSERVED_FAILURE(reasoning: reasoning, failure: observation)`

The reasoning explains the cause of a failure reported by an observation and derives a corrective approach from that explanation.

参数：

- `reasoning: reasoning`：The agent text explaining why the observed failure occurred and what should change.
- `failure: observation`：The observation reporting the failure being explained.

成立条件：

- The observation indicates that an invoked operation did not succeed.
- The reasoning identifies a concrete cause for the failure and states a corrective approach or change based on that cause.

排除条件：

- The reasoning merely notes that something failed without offering a causal explanation.
- The reasoning explains an unrelated issue or offers no corrective direction.

### GUIDES_ACTION

签名：`GUIDES_ACTION(reasoning: reasoning, action: action)`

The action's tool choice, target, or argument values instantiate an intent, diagnosis, or corrected approach explicitly stated in the reasoning.

参数：

- `reasoning: reasoning`：The agent text stating the plan, diagnosis, or corrected approach.
- `action: action`：The action whose tool, target, or arguments carry out that stated approach.

成立条件：

- The reasoning specifies the operation or correction to perform, and the action performs that same operation with matching target or arguments.
- A traceable correspondence exists between the described step and the executed parameters, command, path, or content.

排除条件：

- The action is unrelated to the described step or diverges from it in target or approach.
- The reasoning only reports prior results and the action is merely temporally adjacent.

### USES_OBSERVATION_AS_INPUT

签名：`USES_OBSERVATION_AS_INPUT(action: action, observation: observation)`

The action uses an identifiable value or payload supplied by a prior observation as an operational input.

参数：

- `action: action`：The action receiving the input.
- `observation: observation`：The prior observation supplying the input value or payload.

成立条件：

- An argument, file content, path, or identifier of the action can be traced to content present in the observation.
- The observation precedes the action within the trajectory.

排除条件：

- The observation only guides action selection without supplying an operational input value.
- The nodes are merely temporally adjacent or topically related without a traceable value transfer.

### ATTEMPTS_REPAIR

签名：`ATTEMPTS_REPAIR(repair: action, failure: observation)`

The action re-executes an operation whose prior result was inadequate — reporting an error or failing to produce the intended output — with the command, parameters, or environment changed so as to remove the identified cause.

参数：

- `repair: action`：The action attempting to repair the failure.
- `failure: observation`：The earlier observation reporting the failure or the unusable result.

成立条件：

- The failure observation precedes the repair action and indicates that the operation did not succeed or did not produce the intended result.
- The action preserves the original goal while changing the element identified as faulty, such as an option's argument form, the scope of an environment setting, a path, an executing identity, or source content.

排除条件：

- The action repeats the inadequate invocation without any change.
- The action pursues a different goal unrelated to the reported result.
- No confirming evidence is required for this predicate; confirmation is a separate mechanism.

### CONFIRMS_REPAIR

签名：`CONFIRMS_REPAIR(repair: action, failure: observation, check_result: observation)`

A repair action addresses an observed failure, and a subsequent execution result confirms that the original failure has been resolved.

参数：

- `repair: action`：The action attempting to repair the failure.
- `failure: observation`：The earlier observation reporting the failure.
- `check_result: observation`：The later observation establishing that the original failure no longer occurs.

成立条件：

- The failure precedes the repair, and the repair changes the failing element.
- The later result shows the target operation or content being produced, loaded, or otherwise completed successfully, with no recurrence of the original error.

排除条件：

- The repair is attempted without any later result.
- The later output repeats the original error or otherwise fails to establish resolution.

### REPORTS_FAILURE

签名：`REPORTS_FAILURE(observation: observation)`

The observation indicates that the invoked operation did not succeed.

参数：

- `observation: observation`：The tool result being evaluated for failure.

成立条件：

- The observation carries an error indication, a non-success exit status, or an explicit error message such as a missing file or unloadable module.

排除条件：

- The observation reports successful completion or plain data output without any error indication.

### REPORTS_SUCCESS

签名：`REPORTS_SUCCESS(observation: observation)`

The observation indicates that the invoked operation completed successfully.

参数：

- `observation: observation`：The tool result being evaluated for success.

成立条件：

- The observation contains an explicit success message, a clean completion with no error indication, or a listing of the expected produced artifacts.

排除条件：

- The observation reports an error or non-success exit status.
- The output is only a partial or ambiguous progress message.

### IS_COMPLETION_CONCLUSION

签名：`IS_COMPLETION_CONCLUSION(reasoning: reasoning)`

The reasoning declares the overall objective achieved and cites the verification evidence that supports the claim.

参数：

- `reasoning: reasoning`：The agent text asserting task completion.

成立条件：

- The reasoning states that the requested objective has been fulfilled.
- It references concrete evidence obtained earlier, such as produced artifacts or verified output.

排除条件：

- The reasoning states plans or intermediate steps while work remains.
- The reasoning reports observations without concluding that the objective is achieved.

### IDENTIFIES_MISSING_SOFTWARE_DEPENDENCY

签名：`IDENTIFIES_MISSING_SOFTWARE_DEPENDENCY(reasoning: reasoning, observation: observation)`

The reasoning interprets an environment probe as showing that software required for the task is absent and treats obtaining that software as a prerequisite for proceeding with the intended configuration.

参数：

- `reasoning: reasoning`：The agent text diagnosing the environment and naming the missing capability.
- `observation: observation`：The probe result showing which required tools or services are absent.

成立条件：

- The observation reports probe results about the environment, such as available binaries, packages, or running processes, and shows that one or more task-required tools or services are unavailable.
- The reasoning explicitly connects that absence to the task and indicates that the missing software must be supplied before the intended work can proceed.

排除条件：

- The observation merely enumerates installed software or environment details without revealing a missing task requirement.
- The reasoning restates the task or lists actions without connecting an observed absence to a prerequisite that must be supplied.
- The reasoning explains a failed operation rather than an absent prerequisite.

### ADAPTS_TO_ABSENT_SERVICE_MANAGER

签名：`ADAPTS_TO_ABSENT_SERVICE_MANAGER(reasoning: reasoning, observation: observation)`

The reasoning infers from a process or runtime observation that no conventional service manager or init system is available, and consequently adopts direct or manual control of services instead of the usual management mechanism.

参数：

- `reasoning: reasoning`：The agent text inferring the absence of an init or service manager and adapting the startup strategy.
- `observation: observation`：The process or runtime listing showing that the environment lacks a conventional service manager.

成立条件：

- The observation exposes process or runtime state showing that the environment is not controlled by a conventional init or service manager.
- The reasoning explicitly concludes that services cannot be managed through that absent mechanism and selects direct daemon startup, manual supervision, or an equivalent non-init strategy.

排除条件：

- The observation does not expose process or runtime state relevant to how services are managed.
- The reasoning plans service startup without noting that a management mechanism is absent.
- A service manager is present and the reasoning uses it in the usual way.

### PREPARES_ACCOUNT_FOR_KEY_AUTHENTICATION

签名：`PREPARES_ACCOUNT_FOR_KEY_AUTHENTICATION(action: action)`

The action configures a service account with a usable login environment and a non-locking authentication state, together with key-access ownership and permissions, so the account can be reached remotely without password login and can own the service's data.

参数：

- `action: action`：The account-creation and authentication-state adjustment command or script.

成立条件：

- The action creates or selects an account with a usable login shell and home directory.
- The action places the account's authentication state in a non-locking form so that key-based login is not rejected.
- The action creates a user-owned .ssh directory with restrictive permissions and an authorized-keys file ready to receive public keys.

排除条件：

- The action creates an account but leaves it locked or otherwise unable to accept key-based login.
- The action adjusts unrelated account attributes without preparing remote key-based access.

### INITIALIZES_BARE_REPOSITORY

签名：`INITIALIZES_BARE_REPOSITORY(action: action)`

The action establishes a bare repository as a push target at the intended service location, points its default branch reference at the branch clients will push, and places it under ownership that allows the service account to receive pushes.

参数：

- `action: action`：The repository initialization, branch-reference, and ownership command.

成立条件：

- The action creates a bare repository at the intended service path.
- The action sets HEAD or an equivalent symbolic reference to the designated default branch.
- The action assigns repository ownership or equivalent write authority to the service account.

排除条件：

- The action initializes a non-bare working repository rather than a push target.
- The repository is left without the intended default branch or without ownership permitting the service account to receive pushes.

### CONFIGURES_PUSH_TRIGGERED_DEPLOYMENT

签名：`CONFIGURES_PUSH_TRIGGERED_DEPLOYMENT(action: action)`

The action installs an executable repository hook that reacts to pushed branch references by deploying the pushed content into the directory served by the web server.

参数：

- `action: action`：The hook-writing or hook-installation action.

成立条件：

- The action writes an executable hook into the repository's hook directory.
- The hook logic reads pushed references and performs a work-tree checkout or equivalent deployment into the served document root.
- The hook limits deployment to branch updates and excludes non-branch or branch-deletion events.

排除条件：

- The hook only logs, notifies, or performs an action unrelated to deploying pushed content.
- Deployment into the served directory is not part of the hook behavior.

### CONFIGURES_SERVICE_ENDPOINT

签名：`CONFIGURES_SERVICE_ENDPOINT(action: action)`

The action writes or replaces the active configuration of a network service so that the service listens on the task-required port and serves content from the intended document root.

参数：

- `action: action`：The configuration-writing action that defines the service endpoint.

成立条件：

- The configuration specifies the task-required listen port.
- The configuration specifies the document root from which content should be served.
- The configuration is written to an active configuration location or to one that the service loads.

排除条件：

- The action edits an inactive or sample configuration that the service does not load.
- The action changes unrelated directives without defining the required port and document root.

### PREPARES_DEPLOYMENT_DIRECTORY

签名：`PREPARES_DEPLOYMENT_DIRECTORY(action: action)`

The action prepares the directory served by the web server so that the deployment account can write pushed content into it while the server process retains read access to that content.

参数：

- `action: action`：The directory-creation and ownership or permission adjustment command.

成立条件：

- The action creates the served directory or confirms that it exists.
- The action assigns ownership or permissions that allow the deployment account to write into the directory.
- The resulting ownership and permissions leave the content readable by the web server process.

排除条件：

- The action only reads or lists the directory without preparing it for deployment.
- The action changes ownership or permissions in a way that prevents the web server process from reading deployed content.

### VALIDATES_AND_ENABLES_SERVICE_CONFIGURATION

签名：`VALIDATES_AND_ENABLES_SERVICE_CONFIGURATION(action: action)`

The action confirms that the intended service configuration is enabled and syntactically valid, and makes service startup conditional on that confirmation succeeding.

参数：

- `action: action`：The validation and activation command sequence.

成立条件：

- The action checks whether the intended configuration is enabled or linked into the active configuration set.
- The action runs a syntax or consistency check on the service configuration.
- Startup of the service is chained to the success of the check.

排除条件：

- The service is started without any configuration validation.
- A validation command is run but its failure does not prevent startup.

### STARTS_SERVICE_DAEMONS_DIRECTLY

签名：`STARTS_SERVICE_DAEMONS_DIRECTLY(action: action)`

The action launches the required long-running service daemons directly rather than through a service manager, preparing any runtime prerequisites those daemons need in order to start and remain running.

参数：

- `action: action`：The daemon-launching command or script.

成立条件：

- The action invokes daemon binaries or equivalent direct start commands for the required network services.
- The action prepares runtime prerequisites such as directories, host keys, or runtime state needed for those daemons to start.
- The launched processes are intended to remain running after the invoking command returns.

排除条件：

- The action only installs packages without launching the services.
- The action delegates startup to a service manager or init system.
- The action starts only a transient foreground process instead of the required long-running daemon.

### ESTABLISHES_LOCAL_HOSTNAME_RESOLUTION

签名：`ESTABLISHES_LOCAL_HOSTNAME_RESOLUTION(action: action)`

The action adds a local name-resolution mapping so that the hostname used in the task's client commands resolves to the local or container-reachable address of the service.

参数：

- `action: action`：The hostname or resolver configuration action.

成立条件：

- The action adds or modifies a local hosts-file or equivalent resolver entry.
- The entry maps the task's service hostname to an address that reaches the local service.

排除条件：

- The action changes the machine's own hostname rather than adding a service-name mapping.
- The action only relies on external name resolution without adding the local mapping.

### GUIDES_CONFIGURATION_CHANGE

签名：`GUIDES_CONFIGURATION_CHANGE(observation: observation, action: action)`

An observation exposes the current structure or values of a service configuration, and a subsequent action rewrites that same configuration to the task-required values, using the observed structure to locate or shape the change.

参数：

- `observation: observation`：The observation revealing existing configuration values or activation structure.
- `action: action`：The later action that rewrites the observed configuration.

成立条件：

- The observation shows current configuration details such as a listen directive, a document root, or the active-configuration linkage.
- A subsequent action writes or replaces that same configuration, changing the identified values to the task-required values.
- The correspondence between the observed configuration and the rewritten configuration is identifiable as the same file or the same service configuration.

排除条件：

- The observation supplies an operational data value rather than configuration structure or values.
- The subsequent action modifies an unrelated configuration without using the observed structure or values.
- The action writes a configuration without any prior inspection of that configuration.

### PLANS_END_TO_END_VERIFICATION

签名：`PLANS_END_TO_END_VERIFICATION(reasoning: reasoning)`

The reasoning lays out a forthcoming verification procedure that reproduces the requester's prescribed end-user workflow against the configured system, and identifies the observable outcome by which the procedure's success will be judged.

参数：

- `reasoning: reasoning`：The agent text that specifies the forthcoming validation procedure and its expected outcome.

成立条件：

- The reasoning names at least one end-user interaction from the request, such as authenticating, cloning, committing, pushing, or retrieving the deployed path, as something to be executed for validation.
- The reasoning identifies the observable result that the procedure should produce, so that success can be judged.

排除条件：

- The reasoning only describes configuration changes or service management to be performed.
- The reasoning only reports results of checks already completed, without specifying a forthcoming verification procedure.
- The reasoning plans only an internal or intermediate check that does not exercise the requester's end-user interaction.

### EXECUTES_USER_WORKFLOW_TRIAL

签名：`EXECUTES_USER_WORKFLOW_TRIAL(action: action)`

The action runs the requester's prescribed end-user command sequence, or a faithful stand-in for it, against the configured system as a functional acceptance trial of the delivered capability rather than as configuration or state inspection.

参数：

- `action: action`：The tool invocation that exercises the user-facing flow end to end.

成立条件：

- The invocation contains commands reproducing the end-user interaction from the request, such as a remote clone followed by commit and push, or a retrieval of the deployed path.
- The invocation occurs after the relevant configuration has been applied, so that its result reflects the delivered capability.

排除条件：

- The invocation only edits configuration files, starts services, or inspects filesystem or process state.
- The invocation exercises only an internal component rather than the requester-visible flow.
- The invocation merely prepares or cleans up the trial environment without exercising the user-facing flow.

### OBSERVATION_CONFIRMS_REQUESTED_BEHAVIOR

签名：`OBSERVATION_CONFIRMS_REQUESTED_BEHAVIOR(observation: observation)`

The observation carries the outcome of a user-facing interaction whose content matches the end-user-visible behavior specified in the request, providing direct evidence that the delivered system produces the requested result.

参数：

- `observation: observation`：The tool result carrying the outcome of the user-facing interaction.

成立条件：

- The output contains the result the requester stated they expect, such as served content equal to the specified payload or the expected response from the retrieved resource.
- The result is returned without an error status or failure indication.

排除条件：

- The output shows only configuration, process, or filesystem state.
- The output differs from the requested result, is empty, or reports an error or missing resource.

### OBSERVATION_CONFIRMS_SERVICE_AVAILABILITY

签名：`OBSERVATION_CONFIRMS_SERVICE_AVAILABILITY(observation: observation)`

The observation provides evidence that the required long-running services are active and reachable, through live process entries or through listening-socket entries for the required ports.

参数：

- `observation: observation`：The tool result listing running processes or listening sockets.

成立条件：

- The output shows running process instances for the required daemons, or sockets in the listening state for the required ports.
- The evidence is produced without error markers or missing entries for the required services.

排除条件：

- The output is only a configuration syntax validation or a confirmation that a file was written or edited.
- The output names the services but gives no indication that processes are running or ports are listening.

### ATTRIBUTES_FAILURE_TO_TRIAL_SETUP

签名：`ATTRIBUTES_FAILURE_TO_TRIAL_SETUP(reasoning: reasoning, observation: observation)`

The reasoning concludes that an observed failure originates in the agent's own trial setup or command construction rather than in the delivered system, so no change to the delivered configuration is required.

参数：

- `reasoning: reasoning`：The agent text classifying the origin of the failure.
- `observation: observation`：The tool result reporting the failure whose origin is being classified.

成立条件：

- The reasoning explicitly links the failure to a characteristic of the trial environment or of how the trial command was assembled.
- The reasoning states that the delivered system itself remains correct, or that the failure would not occur for the requester.

排除条件：

- The reasoning treats the failure as a defect of the delivered system.
- The reasoning does not distinguish trial-induced failure from genuine system failure.

### JUDGES_OBSERVATION_CONCLUSIVENESS

签名：`JUDGES_OBSERVATION_CONCLUSIVENESS(reasoning: reasoning, observation: observation)`

The reasoning assesses whether an indirect, low-detail, or empty observation is sufficient to establish the intended property, drawing on auxiliary cues such as reported size, known content, structural knowledge, or tool behavior.

参数：

- `reasoning: reasoning`：The agent text assessing the evidential value of the observation.
- `observation: observation`：The low-detail, empty, or indirect tool result being assessed.

成立条件：

- The reasoning explains why the observation's content, or its absence of output, does or does not establish the target property.
- When the evidence is judged insufficient, the reasoning states what alternative evidence or check is required.

排除条件：

- The reasoning accepts the observation's output at face value without evaluating its sufficiency.
- The reasoning addresses a different observation than the one being judged.

### DELEGATES_OPERATION_TO_RESOURCE_OWNER

签名：`DELEGATES_OPERATION_TO_RESOURCE_OWNER(action: action, rejection: observation)`

In response to a reported ownership or permission refusal, the action performs the rejected operation under the identity that owns the resource instead of the rejected identity.

参数：

- `action: action`：The invocation that re-executes the operation under the owning identity.
- `rejection: observation`：The earlier tool result reporting the ownership or permission error.

成立条件：

- The earlier observation contains an ownership or permission refusal that names the resource.
- The action switches the executing identity to the owning account while preserving the operation's target and intent.

排除条件：

- The earlier error concerns connectivity, availability, or a missing file rather than ownership or permission.
- The action resolves the refusal by changing the resource's ownership or permissions instead of changing the executing identity.
- The action continues to run under the rejected identity.

### CLEANS_TEST_ARTIFACTS

签名：`CLEANS_TEST_ARTIFACTS(action: action)`

The action removes or reverts state created during the agent's own trials — temporary credentials, cloned working copies, scratch directories, trial commits and pushed references, and files deployed by the trials — so the delivered system returns to the pristine state expected immediately before the requester's own first operation, while leaving the configured services and permanent infrastructure intact.

参数：

- `action: action`：The cleanup invocation removing trial-created state.

成立条件：

- The invocation deletes or resets entities that the trials created, such as temporary keys, test clones, scratch directories, test commits or branch references, and files deployed by the trials.
- The invocation restores the initial structural state of the affected locations, such as an empty reference set in the repository, an empty document root, or a credentials file ready to receive the requester's own key.
- The invocation leaves the configured services, account setup, and permanent configuration in place, so the requester's commands still succeed afterwards.

排除条件：

- The invocation only performs routine configuration or service management.
- The invocation deletes resources that belong to the delivered system rather than to the trials.
- The invocation only inspects state without modifying it.
- The reset is performed to repair a reported failure rather than to return the system to its pristine pre-trial state.

### PRESERVES_USER_COMMAND_PRECONDITIONS

签名：`PRESERVES_USER_COMMAND_PRECONDITIONS(reasoning: reasoning)`

The reasoning identifies residual state that would cause the requester's own prescribed commands to fail or misbehave, and concludes that this state must be removed or reverted before handoff.

参数：

- `reasoning: reasoning`：The agent text linking leftover state to a concrete failure in the requester's command sequence.

成立条件：

- The reasoning identifies a specific leftover artifact, such as an already-existing commit or an already-deployed file.
- The reasoning names the concrete command from the request that would fail or misbehave because of that artifact, and calls for reverting it.

排除条件：

- The reasoning argues only for general tidiness without naming a command that would fail.
- The reasoning concludes that the leftover state is harmless for the requester's commands.

### JUSTIFIES_PREPARED_HANDOFF_STATE

签名：`JUSTIFIES_PREPARED_HANDOFF_STATE(reasoning: reasoning)`

The reasoning justifies deliberately leaving a pre-created but empty or inert artifact in place, rather than deleting or pre-populating it, because keeping it lets the requester's own subsequent manual step succeed without extra work.

参数：

- `reasoning: reasoning`：The agent text weighing removal against retention of a prepared artifact.

成立条件：

- The reasoning compares removing the prepared artifact with keeping it in an empty or inert form.
- The reasoning concludes that keeping it lets the requester's own setup step succeed without extra work.

排除条件：

- The reasoning only plans removal of the artifact.
- The reasoning pre-populates functional data that the requester is supposed to supply themselves.

### DERIVES_STATE_FROM_RAW_OUTPUT

签名：`DERIVES_STATE_FROM_RAW_OUTPUT(reasoning: reasoning, observation: observation)`

The reasoning translates low-level, encoded, or procedural output in the observation into an explicit semantic conclusion about the state of the system.

参数：

- `reasoning: reasoning`：The agent text that decodes the raw output into a stated system state.
- `observation: observation`：The tool result containing encoded, numeric, or procedural output such as hexadecimal socket entries and state codes, ref listings, or transfer logs.

成立条件：

- The observation contains tokens that are not directly human-meaningful, such as hexadecimal socket addresses and state codes, encoded status fields, ref listings, or version-control transfer transcripts.
- The reasoning explicitly maps those tokens to named system states, for example which ports are listening, which interfaces the services are bound to, or that a pushed branch was published.
- The stated conclusion is presented as the meaning of the observed output rather than as an independent guess.

排除条件：

- The observation already states a plain semantic conclusion that the reasoning only repeats.
- The reasoning quotes the output without assigning it a system-state meaning.
- The reasoning speculates about system state without grounding the conclusion in the observed tokens.
- The reasoning evaluates whether the observation is sufficient evidence rather than decoding its content.

### INSTALLS_STARTUP_HOOK_FOR_ARTIFACT

签名：`INSTALLS_STARTUP_HOOK_FOR_ARTIFACT(registration_action: action, creation_action: action)`

The later action registers an artifact created by an earlier action in shell, session, or system startup configuration so that the artifact is invoked automatically in future contexts, without altering the artifact's own content.

参数：

- `registration_action: action`：The action that writes or appends startup or session-initialization configuration referencing the artifact.
- `creation_action: action`：The earlier action that created the artifact being registered.

成立条件：

- The creation action produced a named executable, script, or configuration artifact whose creation is evidenced by its result.
- The registration action adds references to that artifact path in one or more startup or session-initialization files, such as a shell rc file, a profile drop-in, or an equivalent.
- The registration action leaves the artifact's content unchanged and only controls when or whether it is invoked.

排除条件：

- The artifact registered was not created by the earlier action in the same trajectory.
- The later action modifies or rewrites the artifact itself instead of registering it.
- The registration only applies an ownership or permission change without arranging automatic invocation.
- The two actions are only temporally adjacent and operationally unrelated.

### EXPLAINS_ANOMALY_AS_HARMLESS

签名：`EXPLAINS_ANOMALY_AS_HARMLESS(reasoning: reasoning, observation: observation)`

The reasoning investigates an anomalous condition visible in the observation, identifies its cause, and concludes that the anomaly does not affect the required functionality, relying on functional evidence rather than altering the configuration.

参数：

- `reasoning: reasoning`：The agent text that diagnoses and judges the anomalous condition.
- `observation: observation`：The tool result exhibiting the anomalous condition.

成立条件：

- The observation shows a condition that deviates from a clean expected state, such as lingering defunct processes, unexpected extra or missing entries, or an unexpectedly empty result.
- The reasoning offers a causal explanation for the anomaly that places its origin outside the delivered functionality.
- The reasoning concludes that the anomaly is cosmetic or non-impacting, citing evidence that the required functionality still succeeds, such as a fresh successful operation or a previously verified user-visible result.

排除条件：

- The anomaly is observed but not explained.
- The anomaly prompts a repair or configuration change.
- The reasoning asserts the condition is harmless without any causal account or functional evidence.
- The reasoning treats the anomaly as a defect of the delivered system.

### RESOLVES_DATA_INCONSISTENCY

签名：`RESOLVES_DATA_INCONSISTENCY(reasoning: reasoning)`

The reasoning detects a discrepancy or conflict among observed data — such as an unexpected mismatch between a container's label and the identifiers or attributes embedded in it — and resolves it by deciding how that data should be interpreted for the task.

参数：

- `reasoning: reasoning`：The agent text detecting the discrepancy and deciding how to interpret the data.

成立条件：

- The reasoning identifies a concrete conflict or unexpected mismatch in the observed data, for example between file names and the identifiers, labels, or attributes found inside them.
- The reasoning weighs the competing interpretations and adopts a decision about which interpretation to use, or concludes that the discrepancy does not affect the task.

排除条件：

- The reasoning merely quotes, summarizes, or reformats the observed data without noticing a discrepancy.
- A discrepancy is noted but its interpretation is left unresolved.
- The observed differences are ordinary expected variation rather than a conflict that requires interpretation.

### DERIVES_CONSTRAINED_SOLUTION

签名：`DERIVES_CONSTRAINED_SOLUTION(reasoning: reasoning)`

The reasoning derives a concrete solution by applying explicit constraints to candidate values, eliminating or comparing alternatives, and selecting a specific result.

参数：

- `reasoning: reasoning`：The agent text deriving the constrained solution.

成立条件：

- The reasoning applies stated constraints, limits, or preferences to candidate values.
- The reasoning compares alternatives or rules them out as infeasible.
- The reasoning states a specific selected solution, including any tie-breaker applied when several candidates remain.

排除条件：

- The reasoning only restates requirements or enumerates raw data.
- A candidate is proposed without being checked against the stated constraints.
- No concrete result is selected.

### GROUNDS_CONCLUSION_IN_OBSERVATION

签名：`GROUNDS_CONCLUSION_IN_OBSERVATION(reasoning: reasoning, observation: observation)`

The reasoning reaches a conclusion or makes a decision that relies on identifiable values, entries, or findings supplied by a prior observation.

参数：

- `reasoning: reasoning`：The reasoning that reaches the conclusion or decision.
- `observation: observation`：The prior observation supplying the substantive content used by the reasoning.

成立条件：

- A conclusion, decision, or derived value in the reasoning can be traced to specific substantive content of the observation.
- The observation precedes the reasoning and contributes data rather than only a success or failure indication.

排除条件：

- The observation only reports tool success or failure without substantive content used by the reasoning.
- The reasoning is only topically related to the observation and does not use its values.
- The conclusion is reached independently of the observation.

### GENERATES_DELIVERABLE_ARTIFACT

签名：`GENERATES_DELIVERABLE_ARTIFACT(action: action)`

The action writes a complete artifact to the task-designated output location, serving as the substantive deliverable of the task.

参数：

- `action: action`：The write action producing the deliverable artifact.

成立条件：

- The action is a write-type operation targeting the output location that the task designates for the deliverable.
- The written content is a complete artifact in the required format carrying the requested payload.

排除条件：

- The action writes an auxiliary script, temporary file, or partial snippet.
- The action reads rather than writes data.
- The action writes outside the designated deliverable location.

### AUTHORS_VALIDATION_PROGRAM

签名：`AUTHORS_VALIDATION_PROGRAM(action: action)`

The action creates or rewrites an executable program whose purpose is to check an artifact or solution against stated requirements and report pass/fail results.

参数：

- `action: action`：The write action authoring the validation program.

成立条件：

- The action writes executable code implementing validation logic.
- The program checks format, constraints, or correctness of an artifact or solution and emits an explicit pass/fail or error outcome.

排除条件：

- The action writes the data deliverable itself rather than a validator.
- The action runs an existing validator without authoring or rewriting its code.
- The action writes prose, data, or an incomplete snippet rather than an executable validation program.

### EXECUTES_VALIDATION_PROGRAM

签名：`EXECUTES_VALIDATION_PROGRAM(action: action)`

The action executes a program or script in order to check an artifact or solution against requirements and obtain verification evidence.

参数：

- `action: action`：The action executing the validation program.

成立条件：

- The tool invocation runs validation logic against an artifact or solution.
- The invocation's purpose is to assess correctness, and its result supplies pass/fail verification evidence.

排除条件：

- The action only reads, writes, or inspects the artifact without running validation logic.
- The action runs a command unrelated to assessing correctness.
- The action only authors validation code without executing it.

### CHECKS_INPUT_INTEGRITY

签名：`CHECKS_INPUT_INTEGRITY(action: action)`

The action performs read-only inspection of task input files' listing, metadata, or checksums in order to confirm that those inputs remain unmodified.

参数：

- `action: action`：The action inspecting the input files for integrity.

成立条件：

- The action inspects existing input files without altering them, for example by listing them with metadata or computing checksums.
- The inspection is aimed at confirming that the task inputs have not been modified.

排除条件：

- The action reads input content for task analysis rather than for verifying that inputs are unchanged.
- The action modifies or deletes input files.
- The action only checks the produced output artifact.
