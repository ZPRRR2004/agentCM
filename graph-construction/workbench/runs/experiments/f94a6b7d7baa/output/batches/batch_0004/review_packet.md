# 第 4 批 Predicate Discovery 结果

## 一、批次信息

处理 Window：31–40
Prompt 版本：v0001
本批新增谓词：19
本批已有谓词修订：5
当前谓词总数：114

## 二、本批新增谓词

### ASSESSES_CANDIDATE_AGAINST_CONSTRAINTS

签名：`ASSESSES_CANDIDATE_AGAINST_CONSTRAINTS(assessment_reasoning: reasoning, candidate_evidence: observation)`

Reasoning considers an identifiable candidate value or fragment supplied by an observation and evaluates whether it satisfies one or more explicitly stated requirements, reaching a judgment of compliance, partial compliance, or violation.

参数：

- `assessment_reasoning: reasoning`：The reasoning that evaluates the candidate against the stated requirements.
- `candidate_evidence: observation`：The observation containing the candidate value or the evidence from which it is extracted.

成立条件：

- The observation contains an identifiable candidate value or fragment.
- The assessment_reasoning refers to at least one explicit requirement and compares the candidate to it.
- The reasoning reaches a conclusion about compliance, partial compliance, or noncompliance.

排除条件：

- The reasoning only extracts or repeats the candidate without evaluating requirements.
- No explicit requirement is applied to the candidate.
- The observation does not contain the candidate being assessed.
- The reasoning evaluates a requirement or deliverable independently of any candidate value.

### VERIFIES_CANDIDATE_BY_TARGETED_REEXTRACTION

签名：`VERIFIES_CANDIDATE_BY_TARGETED_REEXTRACTION(verification_reasoning: reasoning, extraction_action: action, extraction_result: observation)`

A proposed candidate or candidate fragment is checked by re-reading the exact stored location, offset, or field from which it was claimed to originate, and the returned data are compared with the candidate to confirm or refute it.

参数：

- `verification_reasoning: reasoning`：The reasoning selecting the candidate and the exact location or field to re-read.
- `extraction_action: action`：The action that retrieves data from the identified location.
- `extraction_result: observation`：The observation reporting the retrieved data for comparison with the candidate.

成立条件：

- The verification_reasoning identifies a candidate or fragment and a specific location, offset, or field to inspect.
- The extraction_action retrieves data from that identified location rather than performing an untargeted search.
- The extraction_result contains data that can be directly compared with the candidate, confirming or refuting it.

排除条件：

- The action is an untargeted exploration not tied to a proposed candidate.
- The retrieved data cannot be compared with the candidate.
- The reasoning does not identify what is being verified or where it should be found.
- The action independently recomputes the candidate through a different path rather than re-reading the claimed source location.

### EXCLUDES_ALTERNATIVE_CANDIDATES_BY_EXHAUSTIVE_SEARCH

签名：`EXCLUDES_ALTERNATIVE_CANDIDATES_BY_EXHAUSTIVE_SEARCH(exclusion_reasoning: reasoning, exhaustive_search_action: action, search_result: observation)`

Reasoning establishes that a candidate is unique, or that no competing candidate satisfies the relevant criterion, by directing an exhaustive search over the available artifact or corpus and interpreting the search result as excluding alternatives.

参数：

- `exclusion_reasoning: reasoning`：The reasoning that seeks to rule out competing candidates or confirm uniqueness.
- `exhaustive_search_action: action`：The action that enumerates occurrences of a relevant pattern or feature across the available artifact or corpus.
- `search_result: observation`：The observation listing the occurrences found by the search.

成立条件：

- The exclusion_reasoning identifies a need to rule out alternatives or confirm that a candidate is the only qualifying occurrence.
- The exhaustive_search_action searches the relevant artifact or corpus for a pattern or feature rather than checking a single known location.
- The search_result shows that no additional qualifying candidate was found, or that the only qualifying hit is the known candidate, and the reasoning uses this to exclude alternatives.

排除条件：

- The search is limited to a single known location and cannot reveal alternatives.
- The observation reports additional qualifying candidates that are not excluded.
- The search result is not interpreted as relevant to uniqueness or alternative exclusion.
- The reasoning searches for additional context about one already identified match rather than attempting to enumerate competing candidates across the artifact.

### CORROBORATES_CANDIDATE_WITH_INDEPENDENT_METADATA

签名：`CORROBORATES_CANDIDATE_WITH_INDEPENDENT_METADATA(corroboration_reasoning: reasoning, metadata_observation: observation)`

Reasoning uses a separately recorded metadata value, such as a length, size, count, or structural field, that is independent of a proposed candidate's own expression to check the candidate's consistency and thereby corroborate or undermine it.

参数：

- `corroboration_reasoning: reasoning`：The reasoning that compares the candidate with the independent metadata value.
- `metadata_observation: observation`：The observation containing the metadata value used for the consistency check.

成立条件：

- The metadata_observation contains a value that is independent of the candidate's own expression, such as a stored length, size, count, or structural field.
- The corroboration_reasoning compares the candidate or its expected properties with that metadata value.
- The comparison yields a consistency result that the reasoning uses to corroborate or undermine the candidate.

排除条件：

- The metadata is merely the candidate itself or a direct repetition of it.
- The reasoning mentions metadata without comparing it to the candidate.
- No consistency conclusion is drawn from the metadata.
- The metadata is used to generate a new requirement for an action rather than to check an already proposed candidate.

### RECONSTRUCTS_CANDIDATE_FROM_COMPLEMENTARY_FRAGMENTS

签名：`RECONSTRUCTS_CANDIDATE_FROM_COMPLEMENTARY_FRAGMENTS(reasoning: reasoning)`

The reasoning treats two or more partial segments as complementary parts of a single result, combines them into one candidate, and evaluates the combined candidate against at least one whole-candidate constraint such as total length, boundary pattern, allowed character set, or checksum.

参数：

- `reasoning: reasoning`：The reasoning node that identifies the complementary segments, combines them into one candidate, and checks the combined candidate.

成立条件：

- The reasoning identifies at least two partial segments that are treated as complementary parts of the same result rather than as separate results.
- The reasoning combines the segments into a single candidate result.
- The reasoning evaluates the combined candidate against at least one whole-candidate constraint, such as total length, prefix, suffix, allowed character set, or checksum.

排除条件：

- The reasoning deals with only one segment or does not combine segments.
- The reasoning combines segments but does not evaluate the combined candidate against any whole-candidate constraint.
- The segments are not presented as parts of the same candidate result.
- The reasoning merely restates a combined value without any constraint evaluation.

### FORMULATES_IMPLEMENTATION_DESIGN

签名：`FORMULATES_IMPLEMENTATION_DESIGN(design_reasoning: reasoning)`

The reasoning constructs a concrete candidate implementation design, specifying artifact structure, algorithmic components, or syntax/mechanism choices intended to satisfy stated requirements.

参数：

- `design_reasoning: reasoning`：Reasoning that specifies the intended structure, algorithm, or mechanism of a proposed solution.

成立条件：

- The reasoning specifies a concrete solution structure, algorithm, artifact organization, or syntax/mechanism choice rather than only restating a goal.
- The reasoning indicates how at least one specified component or mechanism is expected to contribute to satisfying a stated requirement.

排除条件：

- The reasoning only states that an implementation, inspection, or test will be performed without describing the proposed design.
- The reasoning only evaluates observed results without proposing or constructing a design.
- The reasoning only enumerates requirements or constraints without describing a concrete implementation structure.

### VERIFIES_MULTI_INTERFACE_COMPATIBILITY

签名：`VERIFIES_MULTI_INTERFACE_COMPATIBILITY(verification_reasoning: reasoning, execution_action: action, result_observation: observation)`

The reasoning sets an acceptance requirement that an artifact must operate through multiple specified invocation interfaces or execution paths, the action exercises those paths, and the observation reports successful or equivalent outcomes from them.

参数：

- `verification_reasoning: reasoning`：Reasoning identifying the multiple interfaces or execution paths that must succeed.
- `execution_action: action`：Action exercising the artifact through those interfaces or paths.
- `result_observation: observation`：Observation reporting outcomes from the exercised paths.

成立条件：

- The reasoning identifies at least two specified invocation interfaces or execution paths that the artifact must satisfy.
- The action exercises the artifact through each of those identified paths, optionally across multiple inputs.
- The observation reports outcomes from those paths that can be compared for correctness or equivalence and that demonstrate successful operation.

排除条件：

- Only one invocation interface or execution path is exercised.
- The action only compiles the artifact or checks syntax without executing the required paths.
- The observation does not report outcomes for the paths being compared.
- At least one required path fails or produces an outcome inconsistent with the others, so compatibility is not verified.
- The multiple paths are not identified in the reasoning as an acceptance requirement.

### EXPLAINS_ARTIFACT_BEHAVIOR_FROM_SOURCE

签名：`EXPLAINS_ARTIFACT_BEHAVIOR_FROM_SOURCE(explanation_reasoning: reasoning, source_observation: observation)`

The reasoning explains how an artifact realizes its behavior—including differing behavior across execution contexts—by interpreting specific source constructs present in an observation of the artifact's content.

参数：

- `explanation_reasoning: reasoning`：The reasoning node interpreting source constructs to explain the artifact's behavior.
- `source_observation: observation`：The observation containing the artifact or source content being interpreted.

成立条件：

- The observation contains source or artifact content.
- The reasoning references at least one specific construct, block, directive, or code element in that content.
- The reasoning explains how that construct causes or enables the artifact's behavior, including, where relevant, its differing behavior across execution contexts.

排除条件：

- The reasoning only summarizes test results, restates content, or describes behavior without tying it to specific source constructs.
- The observation does not contain source or artifact content.
- The reasoning references no concrete source construct.

### JUSTIFIES_NUMERICAL_EQUIVALENCE_BY_ERROR_ANALYSIS

签名：`JUSTIFIES_NUMERICAL_EQUIVALENCE_BY_ERROR_ANALYSIS(reasoning: reasoning)`

The reasoning derives or bounds the magnitude of accumulated numerical error expected from a proposed computation and compares that magnitude with the required equivalence tolerance, concluding that the produced results will or will not be accepted as equivalent.

参数：

- `reasoning: reasoning`：The agent text performing the error-magnitude derivation or bound and the comparison against the required tolerance.

成立条件：

- The reasoning quantifies an expected error magnitude or worst-case bound for the proposed computation, for example from the number of accumulation steps and machine epsilon.
- The reasoning explicitly relates that magnitude to the stated tolerance and concludes that the tolerance will or will not be met.

排除条件：

- The reasoning asserts correctness or equivalence without deriving or bounding any error magnitude.
- The quantified quantity concerns something other than numerical accuracy, such as runtime, memory, or cost.
- The error magnitude is only taken from an already reported measurement rather than derived or estimated for the proposed computation.

### PREDICTS_PERFORMANCE_FROM_COMPLEXITY_ESTIMATE

签名：`PREDICTS_PERFORMANCE_FROM_COMPLEXITY_ESTIMATE(reasoning: reasoning)`

The reasoning estimates the time or resource cost of one or more implementations, operations, or commands from operation counts, data sizes, conversion overhead, or algorithmic complexity, and uses that estimate to judge whether a performance requirement will be met or to choose how a command should be executed.

参数：

- `reasoning: reasoning`：The agent text containing the cost, operation-count, or duration estimate and the judgement or execution decision drawn from it.

成立条件：

- The reasoning gives a quantitative cost, operation-count, or duration estimate for at least one implementation, operation, or command, before the corresponding outcome is observed.
- The estimate is used either to conclude that a performance requirement will be met or violated, or to decide how a command should be executed, such as its expected duration, timeout, or background execution.

排除条件：

- The reasoning names a performance requirement without estimating any cost or duration.
- The estimate concerns numerical accuracy or correctness rather than time or resource cost.
- The estimate is stated but no performance judgement or execution decision is drawn from it.

### MIRRORS_REFERENCE_OPERATION_ORDER

签名：`MIRRORS_REFERENCE_OPERATION_ORDER(reasoning: reasoning, observation: observation)`

The reasoning deliberately adopts the evaluation or accumulation order of a reference implementation exposed by an observation, so that the new implementation reproduces the reference's numerical results within the required tolerance.

参数：

- `reasoning: reasoning`：The agent text stating that the new computation follows the reference implementation's order of operations in order to match its results.
- `observation: observation`：The observation containing the reference implementation or its computational procedure, whose operation order can be identified.

成立条件：

- The observation contains an implementation or computational procedure whose sequence of operations can be identified.
- The reasoning explicitly states that the new computation reproduces that same order or sequence of operations.
- The reasoning links the adopted order to matching the reference results within the required tolerance.

排除条件：

- The reasoning only states that results must match, without any reference to reproducing the reference's operation order.
- The referenced content does not describe an implementation or computational procedure.
- The reasoning selects a materially different order for speed or convenience without claiming to reproduce the reference's results through it.

### IMPLEMENTS_DECLARED_PLACEHOLDER_INTERFACE

签名：`IMPLEMENTS_DECLARED_PLACEHOLDER_INTERFACE(implementation_action: action, skeleton_observation: observation)`

A write action supplies the missing bodies of an artifact whose observed skeleton contains explicit unfilled placeholders together with declared interface elements, while preserving those declared names, signatures, and interface contract.

参数：

- `implementation_action: action`：The write action producing the filled-in implementation of the skeleton artifact.
- `skeleton_observation: observation`：The observation showing the artifact with explicit unfilled placeholders and its declared interface elements.

成立条件：

- The observation shows an artifact containing explicit unfilled placeholders or stub bodies together with declared interface elements such as function names, argument order, entry points, or module name.
- The action writes content that supplies those missing bodies while retaining the declared interface elements.

排除条件：

- The action creates a wholly new artifact for which no declared interface was observed.
- The action only reads, inspects, or builds the artifact without supplying the missing bodies.
- The action replaces the declared interface elements with a different interface rather than implementing them.

### VERIFIES_EQUIVALENCE_AGAINST_REFERENCE

签名：`VERIFIES_EQUIVALENCE_AGAINST_REFERENCE(tolerance_reasoning: reasoning, comparison_action: action, deviation_observation: observation)`

The reasoning states a tolerance within which candidate outputs must match an independent reference implementation; the action evaluates candidate and reference computations on identical inputs; and the observation reports quantified deviations or explicit equality that can be judged against that tolerance.

参数：

- `tolerance_reasoning: reasoning`：The agent text stating the required equivalence or tolerance that candidate outputs must meet relative to the reference implementation.
- `comparison_action: action`：The action that runs both the candidate and the reference computation on the same inputs and obtains their differences.
- `deviation_observation: observation`：The observation reporting the quantified differences or explicit equality between candidate and reference outputs.

成立条件：

- The reasoning states a tolerance or equivalence requirement for matching the outputs of an independent reference implementation.
- The action evaluates both the candidate and the reference on identical inputs within the same check.
- The observation reports quantified deviations or explicit equality for the compared quantities, sufficient to judge compliance with the stated tolerance.

排除条件：

- The action runs only the candidate implementation, with no reference computation in the same check.
- The observation reports only an unquantified pass or fail without comparison to reference outputs.
- The comparison uses an absolute expected value rather than an independently computed reference result.
- The reference side merely reuses the candidate's own computation path, so agreement is not informative.

### STAGES_CHEAP_PROBE_BEFORE_COSTLY_VALIDATION

签名：`STAGES_CHEAP_PROBE_BEFORE_COSTLY_VALIDATION(sequencing_reasoning: reasoning, precursor_check_action: action, full_validation_action: action)`

The reasoning orders verification into two tiers, deciding that a fast reduced-scale check is performed first while the expensive full-scale validation is deferred until after that probe, and the corresponding actions execute the reduced check followed by the complete required workload.

参数：

- `sequencing_reasoning: reasoning`：The agent text expressing the intent to run a quick reduced check before the full or expensive validation.
- `precursor_check_action: action`：The action executing the reduced or small-scale check.
- `full_validation_action: action`：The action executing the complete, expensive, required workload after the precursor check.

成立条件：

- The reasoning expresses the intent to perform a quick or small-scale check before the full or expensive validation.
- The precursor action exercises a reduced or small-scale case rather than the complete required workload.
- The full validation action exercises the complete required workload and occurs after the precursor action.

排除条件：

- Only one of the two verification steps is performed.
- The first action already exercises the full workload rather than a reduced case.
- The reasoning does not order the checks by cost or scale.
- The precursor check and the full validation are not linked as stages of the same verification effort.

### BROADENS_VERIFICATION_BEYOND_REQUIRED_CASES

签名：`BROADENS_VERIFICATION_BEYOND_REQUIRED_CASES(reasoning: reasoning)`

The reasoning identifies input conditions or variations that the stated requirements and given test harness do not exercise, and commits to verifying them in order to reduce the risk of undetected failure.

参数：

- `reasoning: reasoning`：The agent text naming extra input variations and stating the intention to test them for additional assurance.

成立条件：

- The reasoning names at least one concrete input variation not exercised by the stated test harness, such as a size edge case, an alternative memory layout, an alternative data type, a malformed input, or an alternative invocation interface.
- The reasoning states that these additional checks will be performed to gain assurance beyond the required tests.

排除条件：

- The reasoning only repeats the tests required by the task specification.
- Additional checks are mentioned without identifying any concrete input variation to be exercised.
- The extra activity substitutes for required verification rather than extending it, with no additional assurance motive stated.

### IDENTIFIES_PERFORMANCE_BOTTLENECK

签名：`IDENTIFIES_PERFORMANCE_BOTTLENECK(reasoning: reasoning)`

The reasoning localizes the dominant share of a measured runtime to a specific stage, component, or operation in the execution pipeline, using timing evidence, and presents that localization as the reason to optimize or redesign that stage.

参数：

- `reasoning: reasoning`：The agent text attributing most of the measured runtime to a specific stage or component and motivating optimization of it.

成立条件：

- The reasoning references a measured runtime, timing breakdown, or comparable quantitative performance evidence.
- The reasoning attributes the dominant cost to an identifiable stage, component, or operation rather than to the system as a whole.
- The reasoning presents the identified bottleneck as the reason to redesign or optimize that stage.

排除条件：

- The reasoning states only that performance is inadequate without locating a dominant cost.
- The reasoning proposes optimizations unrelated to any identified cost contributor.
- The timing evidence is used only to check a threshold, with no stage or component singled out as the dominant cost.

### ANTICIPATES_UNSPECIFIED_EVALUATION_CRITERIA

签名：`ANTICIPATES_UNSPECIFIED_EVALUATION_CRITERIA(reasoning: reasoning)`

The reasoning identifies one or more plausible checks, usage patterns, or evaluation scenarios that an external evaluator, hidden test harness, or checker might apply even though the task specification does not state them, and assesses whether the current solution already satisfies or would survive them.

参数：

- `reasoning: reasoning`：Agent text that names unstated evaluation scenarios an external checker might exercise and assesses the solution's robustness against them.

成立条件：

- The reasoning names at least one specific check, usage pattern, or scenario that is not stated in the provided task requirements.
- The reasoning treats that scenario as a condition an external evaluator or checker might impose on the solution, and assesses whether the solution already handles it or would survive it.

排除条件：

- The reasoning only restates or addresses checks that are explicitly required by the task specification.
- The reasoning merely reports results of checks already executed without hypothesizing an unstated external check.
- The reasoning describes hypothetical environment or user behaviors without connecting them to evaluation or acceptance of the solution.
- The reasoning enumerates a concrete additional input variation and commits to verifying it, rather than assessing robustness against an unstated evaluator check.

### REVISES_HYPOTHESIS_USING_CONTRADICTING_OBSERVATION

签名：`REVISES_HYPOTHESIS_USING_CONTRADICTING_OBSERVATION(prior_reasoning: reasoning, contradicting_observation: observation, revised_reasoning: reasoning)`

A previously stated expectation, hypothesis, or interpretation is replaced or corrected after an observation reports a result incompatible with it, with the revised reasoning explicitly incorporating that contradictory evidence as the reason for the change.

参数：

- `prior_reasoning: reasoning`：The earlier reasoning node stating the expectation, hypothesis, or interpretation that is being revised.
- `contradicting_observation: observation`：The observation reporting a result, error, or measured value that does not match the prior expectation.
- `revised_reasoning: reasoning`：The later reasoning node that corrects or replaces the prior expectation in light of the contradicting observation.

成立条件：

- The prior reasoning asserts a specific expectation, hypothesis, structural assumption, or interpretation that is identifiable.
- The observation reports a result or error that is incompatible with that prior expectation.
- The revised reasoning changes or corrects the prior expectation and refers to the conflicting result as the reason for the change.

排除条件：

- No prior expectation or hypothesis is identifiable in the earlier reasoning.
- The observation adds information without contradicting the prior expectation.
- The revision is unrelated to the observed evidence, or the prior expectation is merely restated unchanged.
- The earlier statement is only a plan of action rather than an expectation or interpretation that could be contradicted.

### DERIVES_DECISION_FROM_MEASURED_RESULT

签名：`DERIVES_DECISION_FROM_MEASURED_RESULT(decision_reasoning: reasoning, measurement_observation: observation)`

The reasoning uses quantitative results reported in an observation to compare candidate options or configurations and select or endorse the one with the more favorable measured outcome, or to establish a measured baseline that a subsequent choice or target must improve upon.

参数：

- `decision_reasoning: reasoning`：The reasoning that compares measured values and makes or endorses a selection, or fixes a numeric baseline for subsequent action.
- `measurement_observation: observation`：The observation reporting the measured values used in the comparison or baseline.

成立条件：

- The observation reports measured quantities, such as metrics, losses, counts, or comparable numeric outcomes, for at least two candidate options or for a quantity used as a baseline.
- The reasoning compares or reuses those quantities to select or endorse a candidate option or to fix a numerical baseline or target for subsequent action.

排除条件：

- The reasoning only repeats the measured numbers without using them to select, endorse, or set a baseline.
- The observation contains no measurement relevant to the decision or baseline.
- The reasoning selects among options using only qualitative considerations with no measured comparison.
- The measurement is used only to check compliance with an already stated external threshold, with no selection among candidates and no baseline derivation.

## 三、本批已有谓词修订

### ASSESSES_CANDIDATE_AGAINST_CONSTRAINTS → ASSESSES_CANDIDATE_AGAINST_CONSTRAINTS

Window：xhigh__password-recovery__window_0003

修订前：

### ASSESSES_CANDIDATE_AGAINST_CONSTRAINTS

签名：`ASSESSES_CANDIDATE_AGAINST_CONSTRAINTS(assessment_reasoning: reasoning, candidate_evidence: observation)`

Reasoning considers an identifiable candidate value or fragment supplied by an observation and evaluates whether it satisfies one or more explicitly stated requirements, reaching a judgment of compliance, partial compliance, or violation.

参数：

- `assessment_reasoning: reasoning`：The reasoning that evaluates the candidate against the stated requirements.
- `candidate_evidence: observation`：The observation containing the candidate value or the evidence from which it is extracted.

成立条件：

- The observation contains an identifiable candidate value or fragment.
- The assessment_reasoning refers to at least one explicit requirement and compares the candidate to it.
- The reasoning reaches a conclusion about compliance, partial compliance, or noncompliance.

排除条件：

- The reasoning only extracts or repeats the candidate without evaluating requirements.
- No explicit requirement is applied to the candidate.
- The observation does not contain the candidate being assessed.
- The reasoning evaluates a requirement or deliverable independently of any candidate value.

修订后：

### ASSESSES_CANDIDATE_AGAINST_CONSTRAINTS

签名：`ASSESSES_CANDIDATE_AGAINST_CONSTRAINTS(assessment_reasoning: reasoning, candidate_evidence: observation)`

The reasoning considers an identifiable candidate value, fragment, or occurrence supplied by observed content and evaluates whether it satisfies one or more explicitly stated requirements, reaching a judgment of compliance, partial compliance, or violation; the candidate may be a value assembled from multiple observed fragments, and the judgment may draw on the candidate's observed surrounding context.

参数：

- `assessment_reasoning: reasoning`：The reasoning that evaluates the candidate against the stated requirements.
- `candidate_evidence: observation`：The observation containing the candidate value, an observed fragment of it, or the surrounding context from which the candidate is extracted or assembled.

成立条件：

- The observation contains an identifiable candidate value, fragment, or occurrence, or content from which the candidate is assembled.
- The assessment_reasoning refers to at least one explicit requirement and compares the candidate to it.
- The reasoning reaches a conclusion about compliance, partial compliance, or noncompliance; noncompliance may include rejecting a spurious occurrence because its observed adjacent context violates the required format or character set.

排除条件：

- The reasoning only extracts or repeats the candidate without evaluating requirements.
- No explicit requirement is applied to the candidate.
- The observation does not contain the candidate or the context used to assess it.
- The reasoning evaluates a requirement or deliverable independently of any candidate value.

### FORMALIZES_CONSTRAINTS_AS_CHECKABLE_CONDITIONS → FORMALIZES_CONSTRAINTS_AS_CHECKABLE_CONDITIONS

Window：xhigh__portfolio-optimization__window_0001

修订前：

### FORMALIZES_CONSTRAINTS_AS_CHECKABLE_CONDITIONS

签名：`FORMALIZES_CONSTRAINTS_AS_CHECKABLE_CONDITIONS(reasoning: reasoning)`

The reasoning converts informally stated requirements or preferences into explicit, mechanically checkable conditions — such as bounds, admissible ranges, or excluded intervals — against which candidate solutions can be accepted or rejected.

参数：

- `reasoning: reasoning`：The reasoning text that restates the stated requirements as testable admissibility conditions or admissible ranges.

成立条件：

- The reasoning derives at least one explicit admissibility condition from the stated requirements rather than restating them verbatim.
- The derived condition is precise enough to accept or reject a candidate solution.

排除条件：

- The reasoning only repeats the original requirement wording without converting it into a testable condition.
- The reasoning merely lists preferences or observations without deriving any admissibility condition.

修订后：

### FORMALIZES_CONSTRAINTS_AS_CHECKABLE_CONDITIONS

签名：`FORMALIZES_CONSTRAINTS_AS_CHECKABLE_CONDITIONS(reasoning: reasoning)`

The reasoning converts requirements or preferences stated in prose into explicit, mechanically checkable conditions — such as numeric thresholds, minimum performance factors, size limits, bounds, admissible ranges, or excluded intervals — against which candidate solutions or produced artifacts can be accepted or rejected.

参数：

- `reasoning: reasoning`：The reasoning text that restates the stated requirements as testable acceptance conditions, thresholds, or admissible ranges.

成立条件：

- The reasoning states at least one explicit acceptance or admissibility condition attributable to the stated requirements, such as a numeric tolerance, a minimum performance factor, a size limit, a bound, or an admissible range.
- The condition is precise enough to accept or reject a candidate solution or produced artifact, or to judge its compliance.

排除条件：

- The reasoning only repeats the original requirement wording without turning it into a condition that can be evaluated against a candidate solution or artifact.
- The reasoning merely lists preferences or observations without deriving any acceptance or admissibility condition.
- The reasoning only reports the result of an already executed check rather than stating a condition to be met.

### COMPARES_MEASURED_VALUE_AGAINST_THRESHOLD → COMPARES_MEASURED_VALUE_AGAINST_THRESHOLD

Window：xhigh__portfolio-optimization__window_0002

修订前：

### COMPARES_MEASURED_VALUE_AGAINST_THRESHOLD

签名：`COMPARES_MEASURED_VALUE_AGAINST_THRESHOLD(reasoning: reasoning, observation: observation)`

The reasoning extracts a quantitative measurement reported in an observation and evaluates it against a stated limit, threshold, or required magnitude, asserting that the measured value satisfies or violates that requirement.

参数：

- `reasoning: reasoning`：The reasoning node that restates the reported measurement and evaluates it against the limit or requirement.
- `observation: observation`：The observation reporting the numeric measurement being evaluated.

成立条件：

- The observation contains a numeric value produced by a measurement, timing, or count.
- The reasoning explicitly relates that value to a stated limit, threshold, or required magnitude and asserts compliance or violation.

排除条件：

- The observation provides only qualitative information and no numeric comparison is made.
- The reasoning reports the numeric value without linking it to any limit or requirement.
- The reasoning compares quantities with each other without invoking a required limit or threshold.

修订后：

### COMPARES_MEASURED_VALUE_AGAINST_THRESHOLD

签名：`COMPARES_MEASURED_VALUE_AGAINST_THRESHOLD(reasoning: reasoning, observation: observation)`

The reasoning extracts a quantitative measurement reported in an observation and evaluates it against a stated limit, threshold, or required magnitude, asserting that the measured value satisfies or violates that requirement; the evaluation may also characterize the size or adequacy of the margin between the measurement and the threshold.

参数：

- `reasoning: reasoning`：The reasoning node that restates the reported measurement and evaluates it against the limit or requirement.
- `observation: observation`：The observation reporting the numeric measurement being evaluated.

成立条件：

- The observation contains a numeric value produced by a measurement, timing, or count.
- The reasoning explicitly relates that value to a stated limit, threshold, or required magnitude and asserts compliance or violation.

排除条件：

- The observation provides only qualitative information and no numeric comparison is made.
- The reasoning reports the numeric value without linking it to any limit or requirement.
- The reasoning compares quantities with each other without invoking a required limit or threshold.

### ADAPTS_PROBE_TO_ELIMINATE_IDENTIFIED_CONFOUND → ADAPTS_PROBE_TO_ELIMINATE_IDENTIFIED_CONFOUND

Window：xhigh__portfolio-optimization__window_0002

修订前：

### ADAPTS_PROBE_TO_ELIMINATE_IDENTIFIED_CONFOUND

签名：`ADAPTS_PROBE_TO_ELIMINATE_IDENTIFIED_CONFOUND(reasoning: reasoning, adapted_action: action)`

The reasoning identifies a specific property of a previously used measurement or probing technique that distorted or constrained the result it produced, and the following action changes the technique in exactly that respect so that a valid measurement of the same quantity becomes possible.

参数：

- `reasoning: reasoning`：The agent text identifying the confound or limitation in the earlier measurement technique and prescribing the adjusted technique.
- `adapted_action: action`：The tool invocation that performs the same measurement with the adjusted technique.

成立条件：

- The reasoning names a specific property of the earlier technique (for example per-invocation startup delay spreading requests apart, sequential rather than concurrent execution, or an unsupported option) that distorted or invalidated the result obtained with it.
- The adapted action differs from the earlier technique in exactly the respect the reasoning identified, so the identified confound no longer applies.
- The reasoning presents the adjustment as the means of obtaining a valid measurement of the same quantity, not as an unrelated new objective.

排除条件：

- The action repeats the same technique without addressing the identified confound.
- The reasoning provides no identifiable flaw or limitation in the previous approach, so no confound is being eliminated.
- The technique is changed only for convenience or to satisfy an unrelated requirement rather than for measurement validity.
- The earlier attempt yielded no interpretable information because the method or tool was unavailable or unparseable; recovering from an unusable check is a distinct mechanism.

修订后：

### ADAPTS_PROBE_TO_ELIMINATE_IDENTIFIED_CONFOUND

签名：`ADAPTS_PROBE_TO_ELIMINATE_IDENTIFIED_CONFOUND(reasoning: reasoning, adapted_action: action)`

The reasoning identifies a specific property of a previously used measurement, verification, or comparison technique—including a flawed reference value, baseline, or probing method—that distorted or constrained the result it produced, and the following action changes that technique or reference in exactly that respect so that a valid measurement or comparison of the same quantity becomes possible.

参数：

- `reasoning: reasoning`：The agent text identifying the confound or limitation in the earlier measurement, verification, or comparison technique and prescribing the adjusted technique or reference.
- `adapted_action: action`：The tool invocation that performs the same measurement or comparison with the adjusted technique or reference.

成立条件：

- The reasoning names a specific property of the earlier technique or reference (for example per-invocation startup delay spreading requests apart, sequential rather than concurrent execution, an unsupported option, a lower-precision reference, or an inappropriate scale or summation order) that distorted or invalidated the result obtained with it.
- The adapted action differs from the earlier technique or reference in exactly the respect the reasoning identified, so the identified confound no longer applies.
- The reasoning presents the adjustment as the means of obtaining a valid measurement or comparison of the same quantity, not as an unrelated new objective.

排除条件：

- The action repeats the same technique or reference without addressing the identified confound.
- The reasoning provides no identifiable flaw or limitation in the previous approach, so no confound is being eliminated.
- The technique is changed only for convenience or to satisfy an unrelated requirement rather than for measurement or comparison validity.
- The earlier attempt yielded no interpretable information because the method or tool was unavailable or unparseable; recovering from an unusable check is a distinct mechanism.

### CHECKS_INPUT_INTEGRITY_WITHOUT_MODIFICATION → CHECKS_INPUT_INTEGRITY_WITHOUT_MODIFICATION

Window：xhigh__pytorch-model-recovery__window_0002

修订前：

### CHECKS_INPUT_INTEGRITY_WITHOUT_MODIFICATION

签名：`CHECKS_INPUT_INTEGRITY_WITHOUT_MODIFICATION(reasoning: reasoning, inspection_action: action, inspection_result: observation)`

The reasoning states the goal of confirming that protected or read-only inputs remain unaltered, a non-mutating inspection action is performed for that purpose, and the resulting observation reports state information bearing on whether those inputs are unchanged.

参数：

- `reasoning: reasoning`：The reasoning text expressing the intention to confirm that the inputs were not modified.
- `inspection_action: action`：The non-mutating action (listing, checksum, or read) applied to the input artifacts.
- `inspection_result: observation`：The observation reporting metadata, checksums, or contents relevant to the inputs' integrity.

成立条件：

- The reasoning states that preserving or confirming the unmodified state of the inputs is the purpose of the check.
- The inspection action does not write to or otherwise alter the inspected inputs.
- The observation reports metadata, checksums, or contents that bear on whether the inputs are unchanged.

排除条件：

- The action modifies the inspected inputs.
- The inspection serves solution production rather than confirming input integrity.
- No observation reports the inspection's outcome.

修订后：

### CHECKS_INPUT_INTEGRITY_WITHOUT_MODIFICATION

签名：`CHECKS_INPUT_INTEGRITY_WITHOUT_MODIFICATION(reasoning: reasoning, inspection_action: action, inspection_result: observation)`

The reasoning states the goal of confirming that protected or read-only inputs, parameters, or components remain unaltered, a non-mutating inspection action is performed for that purpose, and the resulting observation reports state information bearing on whether those protected elements are unchanged or changed only where explicitly permitted.

参数：

- `reasoning: reasoning`：The reasoning text expressing the intention to confirm that the protected inputs, parameters, or components were not modified.
- `inspection_action: action`：The non-mutating action (listing, checksum, read, or comparison) applied to the protected elements.
- `inspection_result: observation`：The observation reporting metadata, checksums, contents, or comparison outcomes relevant to the protected elements' integrity.

成立条件：

- The reasoning states that preserving or confirming the unmodified state of the protected inputs, parameters, or components is the purpose of the check.
- The inspection action does not write to or otherwise alter the inspected elements.
- The observation reports metadata, checksums, contents, or comparison outcomes that bear on whether the protected elements are unchanged or changed only where explicitly permitted.

排除条件：

- The action modifies the inspected elements.
- The inspection serves solution production rather than confirming preservation.
- No observation reports the inspection's outcome.
- No protected element is identified as required to remain unchanged.

## 四、当前完整 Registry

### PLANS_NEXT_ACTION

签名：`PLANS_NEXT_ACTION(reasoning: reasoning)`

The reasoning explicitly expresses an intended future action or sequence of actions that the agent has not yet performed.

参数：

- `reasoning: reasoning`：The reasoning node that states an intended future action or sequence.

成立条件：

- The reasoning explicitly identifies at least one intended future action or step.
- The intended action is presented as something still to be done rather than as already completed.

排除条件：

- The reasoning only reports or summarizes actions already completed.
- The reasoning states a conclusion, diagnosis, or observation summary without expressing future intent.
- The reasoning states only a general goal or desired result without identifying any intended action or step.

### IDENTIFIES_DEFECT_FROM_OBSERVATION

签名：`IDENTIFIES_DEFECT_FROM_OBSERVATION(reasoning: reasoning, observation: observation)`

The reasoning uses identifiable content of an observation to identify a defect, error, or incompleteness in the artifact or state described by that observation.

参数：

- `reasoning: reasoning`：The reasoning node that identifies the defect, error, or gap.
- `observation: observation`：The observation whose content provides evidence of the defective or incomplete state.

成立条件：

- The observation contains identifiable evidence of an incomplete, erroneous, or otherwise defective state.
- The reasoning explicitly characterizes that state as a problem, gap, or defect requiring attention or correction.

排除条件：

- The reasoning merely repeats or describes the observation without identifying a defect.
- The observation does not contain evidence of a defect or gap.
- The reasoning asserts a defect that is not supported by identifiable observation content.

### FORMULATES_CORRECTIVE_SOLUTION

签名：`FORMULATES_CORRECTIVE_SOLUTION(reasoning: reasoning)`

The reasoning derives and specifies a concrete method, content, or set of steps intended to remedy an identified defect or gap.

参数：

- `reasoning: reasoning`：The reasoning node that derives and specifies the corrective method or steps.

成立条件：

- The reasoning refers to an identified defect, gap, or problematic state.
- The reasoning provides at least one concrete corrective step, replacement content, or method intended to address that defect.

排除条件：

- The reasoning only states that a fix is needed without specifying how to perform it.
- The reasoning only summarizes a correction that was already carried out.
- The reasoning only plans to investigate or gather information without formulating a corrective method.

### ACTION_IMPLEMENTS_PLANNED_STEP

签名：`ACTION_IMPLEMENTS_PLANNED_STEP(action: action, reasoning: reasoning)`

The action carries out a step that the reasoning explicitly specified as an intended future action or corrective step.

参数：

- `action: action`：The action performing the planned step.
- `reasoning: reasoning`：The reasoning node specifying the intended step, target, or corrective content.

成立条件：

- The reasoning specifies a future action, target, or corrective content.
- The action performs that specified step using a corresponding operation, target, or content.

排除条件：

- The action is unrelated to the reasoning's stated intent.
- The reasoning only describes an outcome or diagnosis without specifying an action.
- The action is an unplanned reaction that is not described in the reasoning.

### CHECKS_PREREQUISITE_AVAILABILITY

签名：`CHECKS_PREREQUISITE_AVAILABILITY(prerequisite_reasoning: reasoning, check_action: action, check_result: observation)`

The reasoning identifies a tool, resource, or environment capability on which a planned or contemplated action depends, a check action queries that prerequisite's availability, version, or readiness, and the observation reports its status.

参数：

- `prerequisite_reasoning: reasoning`：The reasoning node indicating that a planned or contemplated action depends on a required capability or resource, or that its availability must be verified.
- `check_action: action`：The action that queries availability, version, or readiness of the prerequisite.
- `check_result: observation`：The observation reporting the prerequisite's availability, version, or readiness.

成立条件：

- The reasoning links a planned or contemplated action to a prerequisite tool, resource, capability, or environment condition.
- The check action queries the availability, version, or readiness of that prerequisite rather than performing the planned work itself.
- The observation reports whether the prerequisite is available or ready.

排除条件：

- No planned or contemplated action depends on the checked prerequisite.
- The check action queries something unrelated to the stated dependency.
- The observation does not report availability, version, or readiness of the prerequisite.

### TESTS_ASSUMPTION_WITH_PROBE

签名：`TESTS_ASSUMPTION_WITH_PROBE(probe_action: action, assumption_reasoning: reasoning, probe_result: observation)`

A targeted action tests a specific uncertainty or hypothesis identified in reasoning, and the resulting observation provides interpretable evidence bearing on that uncertainty.

参数：

- `probe_action: action`：The targeted action that probes the uncertainty or hypothesis.
- `assumption_reasoning: reasoning`：The reasoning node identifying the hypothesis, property, or uncertainty being tested.
- `probe_result: observation`：The observation reporting a result relevant to the hypothesis or uncertainty.

成立条件：

- The reasoning identifies a specific uncertainty, hypothesis, or property to be checked.
- The probe action is directed at obtaining evidence about that specific uncertainty.
- The observation reports a result that can be interpreted as evidence about the uncertainty.

排除条件：

- The action is unrelated to the stated uncertainty or hypothesis.
- The observation does not address the uncertainty being tested.
- No identifiable uncertainty or hypothesis motivates the action.

### DIAGNOSES_FAILURE_CAUSE

签名：`DIAGNOSES_FAILURE_CAUSE(reasoning: reasoning, observation: observation)`

The reasoning assigns a specific causal mechanism to a failure or error reported in an observation, explaining how the failure arose rather than merely restating the error text.

参数：

- `reasoning: reasoning`：The reasoning node explaining the cause or mechanism of the failure.
- `observation: observation`：The observation reporting the error or unsuccessful outcome.

成立条件：

- The observation reports an error, non-zero exit status, or otherwise unsuccessful outcome.
- The reasoning identifies a specific cause or mechanism responsible for that failure, going beyond the literal error message.
- The stated cause is consistent with the facts reported in the observation.

排除条件：

- The reasoning merely notes that a failure occurred.
- The reasoning proposes a retry without explaining the cause.
- The reasoning only repeats or paraphrases the error message without explaining it.
- The stated cause contradicts the observation's reported facts.
- The observation does not report a failure or error.

### CORRECTS_FAILED_ACTION_WITH_DIAGNOSIS

签名：`CORRECTS_FAILED_ACTION_WITH_DIAGNOSIS(corrected_action: action, diagnostic_reasoning: reasoning, failure_observation: observation)`

A subsequent action alters the approach, parameters, or resource of an earlier failing action in a way that follows from a diagnosed cause, aiming to overcome the observed failure.

参数：

- `corrected_action: action`：The subsequent action that changes the approach, parameters, or resource.
- `diagnostic_reasoning: reasoning`：The reasoning node diagnosing the cause and identifying the needed change.
- `failure_observation: observation`：The observation reporting the earlier failure or error.

成立条件：

- The failure observation reports an unsuccessful action or error.
- The reasoning diagnoses the cause of the failure and identifies a needed change.
- The corrected action implements the relevant change in parameter, resource, or approach.

排除条件：

- The subsequent action repeats the failed action without a relevant change.
- The action is not based on the diagnosed cause.
- The observation does not report a failure or error.

### CONFIRMS_EXPECTED_OUTCOME_FROM_OBSERVATION

签名：`CONFIRMS_EXPECTED_OUTCOME_FROM_OBSERVATION(reasoning: reasoning, observation: observation)`

The reasoning interprets an observation as confirming that an expected condition, success criterion, or intended outcome has been achieved.

参数：

- `reasoning: reasoning`：The reasoning node interpreting the observation as confirmation.
- `observation: observation`：The observation providing evidence that matches the expected outcome.

成立条件：

- The reasoning states or implies an expected outcome or success criterion.
- The observation contains identifiable evidence matching that expectation.
- The reasoning explicitly treats the observation as confirmation that the expected outcome holds.

排除条件：

- The observation is used only as an input to further action rather than as confirmation.
- The reasoning merely predicts an outcome without checking it against an observation.
- The observation is ambiguous or unrelated to the expected condition.

### GROUNDS_CONCLUSION_IN_OBSERVATION

签名：`GROUNDS_CONCLUSION_IN_OBSERVATION(reasoning: reasoning, observation: observation)`

The reasoning draws an explicit conclusion, diagnosis, or assessment that is supported by identifiable content of the observation.

参数：

- `reasoning: reasoning`：The reasoning node expressing the conclusion, diagnosis, or assessment.
- `observation: observation`：The observation supplying evidence for that conclusion.

成立条件：

- The reasoning states a conclusion, diagnosis, or assessment beyond merely restating the observation.
- The conclusion depends on specific identifiable content of the observation, such as presence or absence of items, status, version, or output.

排除条件：

- The reasoning repeats or describes the observation without inferring anything from it.
- The observation is unrelated to the conclusion or contains no information that supports it.
- The conclusion rests only on prior knowledge with no identifiable evidential link to the observation.

### IDENTIFIES_MISSING_PREREQUISITE

签名：`IDENTIFIES_MISSING_PREREQUISITE(reasoning: reasoning, observation: observation)`

The reasoning identifies a capability, component, account, resource, or configuration that the goal requires but that is absent or insufficient, using identifiable content of the observation as evidence of the gap.

参数：

- `reasoning: reasoning`：The reasoning node stating that something required for the goal is missing or inadequate.
- `observation: observation`：The observation providing evidence of the absence or insufficiency.

成立条件：

- The reasoning states that something needed for the task is missing, unavailable, or inadequate.
- The observation contains identifiable evidence of the absence or insufficiency, such as a failed lookup, empty listing, missing binary, or missing package.

排除条件：

- The reasoning merely notes a fact without linking it to a requirement of the goal.
- No requirement or gap is stated.
- The observation does not show absence or insufficiency of the required item.

### CONFIGURES_EVENT_TRIGGERED_AUTOMATION

签名：`CONFIGURES_EVENT_TRIGGERED_AUTOMATION(action: action)`

The action creates or updates a configuration artifact that associates a specified event with a downstream operation, so that later occurrences of the event automatically cause that operation without further manual invocation.

参数：

- `action: action`：The action node that writes or installs the automation configuration.

成立条件：

- The action writes or installs a hook, trigger, listener, job, or equivalent automation configuration.
- The configuration content associates a specified event or condition with a downstream operation to be performed automatically.

排除条件：

- The action performs a one-off operation with no persistent trigger.
- The action only documents a procedure for later manual execution.
- The configured artifact does not connect an event or condition to an automatic response.

### MITIGATES_ANTICIPATED_FAILURE

签名：`MITIGATES_ANTICIPATED_FAILURE(risk_reasoning: reasoning, mitigation_action: action, state_observation: observation)`

Reasoning identifies a foreseeable failure mode that could prevent the goal, an action applies a preventive measure addressing that failure mode before it occurs, and an observation provides evidence that the preventive measure is in place.

参数：

- `risk_reasoning: reasoning`：The reasoning node naming the anticipated failure mode or pitfall and its relevance to the goal.
- `mitigation_action: action`：The action node applying a preventive measure against that failure mode.
- `state_observation: observation`：The observation node showing evidence consistent with the preventive measure having been applied.

成立条件：

- The risk_reasoning names a specific failure mode or pitfall that could prevent the goal, rather than a vague risk.
- The mitigation_action changes configuration, permissions, or state in a way that prevents or reduces that failure mode before it occurs.
- The state_observation contains evidence consistent with the mitigation being applied.

排除条件：

- The reasoning only mentions a general risk without a corresponding preventive action.
- The action does not address the identified failure mode, or addresses it only after the failure occurred.
- The observation does not show the mitigated state.

### VALIDATES_CONFIGURATION_BEFORE_ACTIVATION

签名：`VALIDATES_CONFIGURATION_BEFORE_ACTIVATION(validation_reasoning: reasoning, validation_action: action, validation_observation: observation)`

A validation operation checks an artifact, configuration, or prepared state for validity before the dependent component is activated or otherwise relied upon, and the observation confirms that validation succeeded.

参数：

- `validation_reasoning: reasoning`：The reasoning node indicating that the artifact or configuration should be validated before activation or reliance.
- `validation_action: action`：The action performing a configuration test, syntax check, or equivalent validity check; activation may occur in the same action or a subsequent one.
- `validation_observation: observation`：The observation reporting the validation result.

成立条件：

- The validation reasoning or validation action indicates a validation step is to be performed before the component is activated or relied upon.
- The validation action executes a configuration test, syntax check, or equivalent validity check on the artifact, configuration, or prepared state.
- The validation observation reports a successful validation result, and activation or reliance follows that success.

排除条件：

- The component is activated or relied upon without any preceding validation step.
- The validation fails or its result is not interpretable as success.
- Only a post-activation inspection is performed, with no pre-activation or pre-reliance check.

### PREDICTS_RESIDUAL_ARTIFACT_INTERFERENCE

签名：`PREDICTS_RESIDUAL_ARTIFACT_INTERFERENCE(reasoning: reasoning)`

The reasoning predicts that residual state left behind by the agent's own activity will interfere with a later required operation or acceptance condition, and uses that prediction as the reason to remove or reset the residual state before handoff or completion.

参数：

- `reasoning: reasoning`：The agent text that identifies residual self-created state, predicts its adverse effect on a later operation or acceptance condition, and motivates its removal or reset.

成立条件：

- The reasoning identifies specific residual state produced by the agent's own activity, such as files, branches, keys, test data, or configuration changes.
- The reasoning predicts a concrete adverse consequence for a later operation or acceptance condition, such as a failure, mismatch, or misleading check.
- The reasoning treats that prediction as the justification for removing or resetting the identified state before handoff or completion.

排除条件：

- The reasoning expresses only generic cleanliness or tidiness concerns without a predicted operational consequence.
- The predicted consequence concerns state the agent did not create, or state unrelated to its own activity.
- The reasoning plans cleanup solely because the state is no longer needed, with no predicted interference with a later operation or acceptance condition.

### ATTRIBUTES_FAILURE_TO_TEST_HARNESS_ARTIFACT

签名：`ATTRIBUTES_FAILURE_TO_TEST_HARNESS_ARTIFACT(reasoning: reasoning, observation: observation)`

The reasoning classifies a failure observed during the agent's own verification, probe, or simulated execution as an artifact of its test instrumentation or simulated conditions rather than as a defect in the delivered system, distinguishing test-side conditions from the conditions under which the end user or external checker will operate.

参数：

- `reasoning: reasoning`：The agent text that reinterprets the observed failure as a test-side artifact.
- `observation: observation`：The observation reporting the failure whose origin is being classified.

成立条件：

- The observation reports a failure that occurred during the agent's own verification, probe, or simulation procedure.
- The reasoning states that the failure originates in the test setup, test instrumentation, simulated inputs, ad hoc invocation, or missing test-side configuration rather than in the delivered system.
- The reasoning contrasts the test-side conditions with the conditions under which the end user or external checker will operate.

排除条件：

- The reasoning treats the failure as a genuine defect in the delivered configuration or state.
- The reasoning makes no distinction between test-side and user-side conditions.
- The reasoning reports the failure without interpreting where it originated.

### ENUMERATES_REQUIRED_END_STATE

签名：`ENUMERATES_REQUIRED_END_STATE(reasoning: reasoning)`

The reasoning enumerates multiple checkable conditions that the delivered environment must satisfy at handoff, decomposing the final state into individually verifiable invariants rather than listing actions to perform.

参数：

- `reasoning: reasoning`：The agent text listing the conditions the final environment must satisfy.

成立条件：

- The reasoning lists multiple distinct conditions the final environment must satisfy, such as services running, repository empty, keys removed, and host entries present.
- The listed conditions are phrased as verifiable properties of the resulting state rather than as steps to execute.

排除条件：

- The reasoning describes a sequence of actions to execute without stating the resulting state conditions.
- The reasoning states only a single observation about the current state, with no enumeration of required end-state properties.

### IMPLEMENTS_GUARDED_RECOVERY

签名：`IMPLEMENTS_GUARDED_RECOVERY(resilience_reasoning: reasoning, creation_action: action, creation_result: observation)`

The reasoning establishes that a required capability must survive interruption or restart, and an action creates a repeatable, guard-checked mechanism that restores that capability only when it is absent while avoiding failure or disruptive output, with an observation confirming creation of the mechanism.

参数：

- `resilience_reasoning: reasoning`：The agent text identifying the need for the required capability to be restored after restart or interruption.
- `creation_action: action`：The action creating the guarded recovery mechanism.
- `creation_result: observation`：The observation confirming that the mechanism was created and made usable.

成立条件：

- The reasoning frames the mechanism as a safety net keeping a required capability available across restarts, rather than as a one-time start of that capability.
- The created mechanism includes a presence check so that an already-running capability is not duplicated or restarted.
- The mechanism is specified to fail safely and to avoid output or side effects that disrupt the invoking context.
- The observation reports successful creation of the mechanism.

排除条件：

- The mechanism unconditionally starts the capability regardless of whether it is already running.
- The mechanism can fail or emit output that affects the calling context.
- The intent is a one-time activation of the capability with no restart or resilience rationale.

### RECOVERS_CHECK_WITH_ALTERNATIVE_METHOD

签名：`RECOVERS_CHECK_WITH_ALTERNATIVE_METHOD(inconclusive_result: observation, method_diagnosis: reasoning, alternative_action: action)`

An executed check fails to yield usable information — because it produced an empty, missing, or unparseable result, or because the tool or command it depends on is unavailable or unsupported — the reasoning attributes that failure to a concrete limitation of the check's method or tooling rather than to the inspected state, and a follow-up action retrieves the intended information using a materially different technique.

参数：

- `inconclusive_result: observation`：The observation reporting the empty, missing, unparseable, or erroring result of the original check, including an error stating that the command or tool the check relies on is unavailable.
- `method_diagnosis: reasoning`：The reasoning explaining which property of the check's method or tooling (unsupported syntax, wrong format, an unavailable command, or similar) caused the unusable result.
- `alternative_action: action`：The follow-up action that retrieves the intended information through a materially different technique.

成立条件：

- The observation reports that the original check produced no interpretable information, such as empty output, absent entries, an unparseable result, or an error indicating that the command or tool the check relies on is not found or otherwise unavailable.
- The reasoning identifies a concrete limitation of that check's method or tooling, for example unsupported syntax, symlink handling, a wrong format, or an unavailable command, as the cause of the unusable result.
- The alternative action targets the same information as the original check and uses a materially different technique or invocation than the original check.

排除条件：

- The reasoning attributes the unusable result to an actual defect or genuine absence in the inspected system rather than to its method or tooling.
- The follow-up action repeats the same method or only cosmetic variations of it.
- No reasoning distinguishes a tooling artifact from a genuine finding about the inspected state.
- The observation already supplies the intended information, so no alternative retrieval is required.

### REPRODUCES_STIPULATED_WORKFLOW

签名：`REPRODUCES_STIPULATED_WORKFLOW(validation_reasoning: reasoning, replay_action: action)`

The action replays the exact procedure stipulated by the task or requester, mirroring its steps instead of substituting a proxy check, so that the stipulated procedure itself is validated.

参数：

- `validation_reasoning: reasoning`：The reasoning stating that the stipulated procedure itself is being replayed for validation.
- `replay_action: action`：The action whose operations reproduce the stipulated steps.

成立条件：

- The reasoning states that the procedure the requester is expected to run is itself being replayed in order to validate it.
- The action contains the same operations, in the same sequence or spirit, as the stipulated procedure rather than an indirect substitute such as a status query or configuration inspection.

排除条件：

- The action performs an equivalent but different check that does not reproduce the stipulated sequence.
- The reasoning does not connect the action to the stipulated procedure.
- The action merely inspects state or configuration without exercising the user-facing workflow.

### SELECTS_SUBSTITUTE_APPROACH_UNDER_CONSTRAINT

签名：`SELECTS_SUBSTITUTE_APPROACH_UNDER_CONSTRAINT(constraint_reasoning: reasoning, substitute_action: action)`

The reasoning identifies an imposed constraint — an unavailable facility or a restricting rule on how an operation may be performed — weighs how the intended effect can still be achieved within that constraint, and justifies the alternative approach that the associated action then implements.

参数：

- `constraint_reasoning: reasoning`：The reasoning identifying the limitation or restricting rule and justifying the chosen alternative.
- `substitute_action: action`：The action implementing the justified alternative approach.

成立条件：

- The reasoning explicitly identifies an unavailable tool, capability, or an imposed rule or restriction that blocks or forbids the obvious approach.
- The reasoning considers one or more alternatives and explains why the selected alternative achieves the intended effect while respecting that constraint.
- The associated action implements the approach the reasoning justifies.

排除条件：

- The reasoning describes the action without any stated constraint motivating the choice.
- The action does not correspond to the approach the reasoning justifies.
- The reasoning selects the action form for efficiency or convenience without citing a restricting rule or an unavailable facility.
- The reasoning performs an ordinary step with no restricting condition and no alternative weighed against it.

### AUDITS_MULTIPLE_INVARIANTS

签名：`AUDITS_MULTIPLE_INVARIANTS(checklist_reasoning: reasoning, audit_action: action, audit_result: observation)`

The reasoning enumerates several independent conditions that the environment must satisfy, a single action evaluates those conditions together, and the observation reports outcomes attributable to the individual conditions.

参数：

- `checklist_reasoning: reasoning`：The reasoning listing the independent conditions the audit must cover.
- `audit_action: action`：The action evaluating the listed conditions together in one invocation.
- `audit_result: observation`：The observation reporting per-condition results of the audit.

成立条件：

- The reasoning enumerates at least two independent conditions or invariants to be verified.
- The audit action probes multiple of those enumerated conditions within a single invocation.
- The observation reports results that can be attributed to individual conditions rather than a single undifferentiated status.

排除条件：

- Only a single condition is checked.
- The observation aggregates outcomes so that individual conditions cannot be distinguished.
- The action does not actually probe the enumerated conditions.

### RESETS_TO_PRISTINE_STATE_FOR_HANDOFF

签名：`RESETS_TO_PRISTINE_STATE_FOR_HANDOFF(handoff_reasoning: reasoning, reset_action: action)`

The reasoning explains that the environment should be returned to its initial or clean condition so that subsequent use by the recipient behaves without conflicts, and the action removes or empties artifacts produced during the work while leaving required configuration or infrastructure intact.

参数：

- `handoff_reasoning: reasoning`：The reasoning justifying restoring the initial or clean state before handing the environment over.
- `reset_action: action`：The action deleting, emptying, or reverting the artifacts created during the work.

成立条件：

- The reasoning states that the environment is being returned to its starting, empty, or clean condition for the benefit of subsequent use.
- The reset action removes or empties artifacts created during the work.
- The reset action preserves the configured infrastructure or deliverables that the recipient needs.

排除条件：

- Artifacts are deleted for ordinary tidiness without a stated handoff or subsequent-use rationale.
- The action reverts required configuration or deliverables rather than only produced data.
- The reasoning does not address the state in which the environment is left.

### FORMALIZES_CONSTRAINTS_AS_CHECKABLE_CONDITIONS

签名：`FORMALIZES_CONSTRAINTS_AS_CHECKABLE_CONDITIONS(reasoning: reasoning)`

The reasoning converts requirements or preferences stated in prose into explicit, mechanically checkable conditions — such as numeric thresholds, minimum performance factors, size limits, bounds, admissible ranges, or excluded intervals — against which candidate solutions or produced artifacts can be accepted or rejected.

参数：

- `reasoning: reasoning`：The reasoning text that restates the stated requirements as testable acceptance conditions, thresholds, or admissible ranges.

成立条件：

- The reasoning states at least one explicit acceptance or admissibility condition attributable to the stated requirements, such as a numeric tolerance, a minimum performance factor, a size limit, a bound, or an admissible range.
- The condition is precise enough to accept or reject a candidate solution or produced artifact, or to judge its compliance.

排除条件：

- The reasoning only repeats the original requirement wording without turning it into a condition that can be evaluated against a candidate solution or artifact.
- The reasoning merely lists preferences or observations without deriving any acceptance or admissibility condition.
- The reasoning only reports the result of an already executed check rather than stating a condition to be met.

### SELECTS_CANDIDATE_BY_CONSTRAINT_ELIMINATION

签名：`SELECTS_CANDIDATE_BY_CONSTRAINT_ELIMINATION(reasoning: reasoning)`

The reasoning evaluates multiple candidate options, explicitly rejects those that violate stated hard requirements, and identifies a surviving candidate as the selected outcome, optionally using soft preferences only to break ties among survivors.

参数：

- `reasoning: reasoning`：The reasoning text that enumerates candidate options, rejects violating ones, and names the selected option.

成立条件：

- The reasoning considers more than one candidate option.
- At least one candidate is rejected with an explicit reason tied to a hard requirement.
- A surviving candidate is identified as the selected outcome.

排除条件：

- The reasoning asserts a chosen option without evaluating any alternative.
- The reasoning enumerates candidates but never reaches a selection.
- Rejections are based on arbitrary or unstated grounds rather than on stated requirements.

### DERIVES_CONSTRAINT_INPUTS_FROM_OBSERVED_RECORDS

签名：`DERIVES_CONSTRAINT_INPUTS_FROM_OBSERVED_RECORDS(reasoning: reasoning, observation: observation)`

The reasoning extracts specific values from the content of an observation and transforms them into derived quantities, such as occupied intervals, ranges, totals, or parsed records, that serve as inputs constraining the subsequent solution or decision.

参数：

- `reasoning: reasoning`：The reasoning text that extracts values from observed records and computes derived quantities from them.
- `observation: observation`：The observation whose content supplies the underlying records or values being transformed.

成立条件：

- The reasoning cites or transforms specific content present in the observation.
- The derived quantities are used as inputs to the subsequent constraint evaluation or decision rather than merely described.

排除条件：

- The reasoning discusses the observation only in general terms without extracting concrete values.
- The observation's content is not used in the derived quantities.
- The reasoning only restates the observation's content without computing anything from it.

### DETECTS_OBSERVED_DATA_INCONSISTENCY

签名：`DETECTS_OBSERVED_DATA_INCONSISTENCY(reasoning: reasoning, observation: observation)`

The reasoning identifies an explicit discrepancy between the content of an observation and what its labeling, structure, or surrounding context led the agent to expect, and states that discrepancy as a finding.

参数：

- `reasoning: reasoning`：The reasoning text that names the mismatch between observed content and the expectation.
- `observation: observation`：The observation whose content contains the unexpected or inconsistent element.

成立条件：

- The reasoning states what was expected and what was actually observed.
- The inconsistency is attributable to identifiable content in the observation.

排除条件：

- The reasoning only summarizes the observation without comparing it to an expectation.
- The claimed mismatch is between two reasoning statements rather than traced to the observation's content.
- No expectation about the observation's content is articulated.

### CHECKS_INPUT_INTEGRITY_WITHOUT_MODIFICATION

签名：`CHECKS_INPUT_INTEGRITY_WITHOUT_MODIFICATION(reasoning: reasoning, inspection_action: action, inspection_result: observation)`

The reasoning states the goal of confirming that protected or read-only inputs, parameters, or components remain unaltered, a non-mutating inspection action is performed for that purpose, and the resulting observation reports state information bearing on whether those protected elements are unchanged or changed only where explicitly permitted.

参数：

- `reasoning: reasoning`：The reasoning text expressing the intention to confirm that the protected inputs, parameters, or components were not modified.
- `inspection_action: action`：The non-mutating action (listing, checksum, read, or comparison) applied to the protected elements.
- `inspection_result: observation`：The observation reporting metadata, checksums, contents, or comparison outcomes relevant to the protected elements' integrity.

成立条件：

- The reasoning states that preserving or confirming the unmodified state of the protected inputs, parameters, or components is the purpose of the check.
- The inspection action does not write to or otherwise alter the inspected elements.
- The observation reports metadata, checksums, contents, or comparison outcomes that bear on whether the protected elements are unchanged or changed only where explicitly permitted.

排除条件：

- The action modifies the inspected elements.
- The inspection serves solution production rather than confirming preservation.
- No observation reports the inspection's outcome.
- No protected element is identified as required to remain unchanged.

### DECOMPOSES_TASK_INTO_SUBGOALS

签名：`DECOMPOSES_TASK_INTO_SUBGOALS(reasoning: reasoning)`

The reasoning breaks an overall task into two or more distinct subgoals, questions, or procedural steps that stand in an ordering or dependency relationship and can guide subsequent execution.

参数：

- `reasoning: reasoning`：The reasoning node that decomposes the overall task into subgoals or procedural steps.

成立条件：

- The reasoning identifies at least two distinct subgoals, questions, or procedural steps.
- The subgoals or steps are presented with an ordering, dependency, or execution relationship rather than as an unrelated collection.
- The decomposition is derived from the stated task and is specific enough to guide execution.

排除条件：

- The reasoning identifies only a single intended action or subgoal.
- The reasoning merely restates the overall task without dividing it into executable parts.
- The reasoning lists unrelated facts or observations that are not presented as parts of the task.

### OPERATIONALIZES_UNDERSPECIFIED_REQUIREMENT

签名：`OPERATIONALIZES_UNDERSPECIFIED_REQUIREMENT(reasoning: reasoning)`

The reasoning recognizes an ambiguous or underspecified aspect of a requirement and commits to a concrete, executable interpretation — such as which fields to process, which filter condition to apply, which metric to compute, or which tool to use — that can guide the procedure.

参数：

- `reasoning: reasoning`：The reasoning node that resolves an ambiguity or underspecification into an operational interpretation.

成立条件：

- The reasoning identifies an ambiguity, an alternative reading, or an underspecified aspect of the requirement.
- The reasoning commits to a concrete operational definition or procedure rather than leaving the ambiguity open.
- The selected interpretation is specific enough to determine which data, condition, metric, or tool will be used.

排除条件：

- The requirement is already fully specified and the reasoning only restates it.
- The reasoning notes an ambiguity but does not resolve it into an operational definition.
- The reasoning supplies procedural detail that is not tied to interpreting the requirement.

### REMEDIES_MISSING_CAPABILITY

签名：`REMEDIES_MISSING_CAPABILITY(gap_reasoning: reasoning, provisioning_action: action, confirmation_observation: observation)`

The reasoning identifies a specific prerequisite that the task requires but that is absent, stale, or otherwise insufficient — such as a missing tool, library, package, credential, or an unprepared configuration or package index; a provisioning action installs, fetches, refreshes, or otherwise supplies that prerequisite; and an observation confirms that the prerequisite has become available.

参数：

- `gap_reasoning: reasoning`：The reasoning node identifying the prerequisite that is missing, stale, or otherwise insufficient and required for the task.
- `provisioning_action: action`：The action that installs, fetches, refreshes, or otherwise provisions the identified prerequisite.
- `confirmation_observation: observation`：The observation reporting that the prerequisite has been installed, prepared, or is now available.

成立条件：

- The reasoning identifies a specific prerequisite — a dependency, tool, library, package, credential, or an insufficient configuration or index state — as missing or inadequate and required for the task.
- The provisioning action is directed at supplying, installing, or refreshing that identified prerequisite rather than at performing the task's primary work itself.
- The observation reports successful installation, successful preparation, or confirmed availability of the prerequisite.

排除条件：

- No specific missing or inadequate prerequisite is identified.
- The action does not provision the identified prerequisite, or merely retries the previously failing operation without supplying anything.
- The observation does not confirm availability, or the provisioning outcome is left unknown.
- The action provisions something merely convenient rather than a prerequisite identified as required for the task.

### TRANSLATES_SCHEMA_EVIDENCE_INTO_PROCESSING_PROCEDURE

签名：`TRANSLATES_SCHEMA_EVIDENCE_INTO_PROCESSING_PROCEDURE(schema_observation: observation, interpretation_reasoning: reasoning, implementation_action: action)`

An observation supplies structural, schema, field-list, format, or documented layout information about a resource; the reasoning uses that structural information to determine which fields, parameters, or operations the task requires; and an action creates or executes a procedure that implements that determination.

参数：

- `schema_observation: observation`：The observation containing schema, field, format, or documented layout information about the resource.
- `interpretation_reasoning: reasoning`：The reasoning that maps the task requirements onto the fields, parameters, or operations indicated by the structural evidence.
- `implementation_action: action`：The action creating or executing a procedure that implements the determined interpretation.

成立条件：

- The observation contains structural, schema, field-list, format, or documented layout information relevant to the resource.
- The reasoning explicitly uses that structural information to determine which fields, parameters, or operations the task requires.
- The action creates or executes a procedure that operationalizes the interpretation rather than merely retrieving or inspecting data.

排除条件：

- The observation contains only values or results without structural or schema information.
- The reasoning does not reference the structural or field information when determining the procedure.
- The action retrieves or inspects data but does not implement a procedure derived from the structural evidence.

### SURVEYS_ENVIRONMENT_STATE_FOR_PLANNING

签名：`SURVEYS_ENVIRONMENT_STATE_FOR_PLANNING(planning_reasoning: reasoning, exploratory_action: action, state_observation: observation)`

The reasoning indicates that some environment or resource state is unknown, unchecked, or relevant to planning; a reconnaissance action inspects, lists, or queries that state; and the resulting observation reports state information that can inform subsequent decisions.

参数：

- `planning_reasoning: reasoning`：The reasoning node indicating that environment or resource state is unknown, must be checked, or is relevant to planning.
- `exploratory_action: action`：The action performing an inspection, listing, or query of the environment or resource state.
- `state_observation: observation`：The observation reporting the inspected environment or resource state.

成立条件：

- The reasoning indicates that some environment or resource state is unknown, must be checked, or is relevant to planning.
- The exploratory action inspects, lists, or queries that environment or resource state rather than performing a substantive transformation or final computation.
- The observation reports state information relevant to subsequent planning or decisions.

排除条件：

- The action performs a substantive transformation or final computation rather than an inspection of state.
- The reasoning already has the relevant state and expresses no reconnaissance need.
- The observation is unrelated to the environment or resource state being surveyed.

### CORROBORATES_RESULT_WITH_INDEPENDENT_PATH

签名：`CORROBORATES_RESULT_WITH_INDEPENDENT_PATH(baseline_result: observation, validation_action: action, validation_result: observation)`

A previously obtained result is recomputed through a materially different data-access or implementation path in order to check for agreement, and the second observation reproduces the same value for the same quantity.

参数：

- `baseline_result: observation`：The observation reporting the first computed value produced by the original implementation path.
- `validation_action: action`：The action recomputing the same quantity through a materially different data-access or implementation path.
- `validation_result: observation`：The observation reporting the recomputed value obtained from the alternative path.

成立条件：

- The baseline observation reports a specific computed value.
- The validation action uses a different loading, access, or implementation path than the one that produced the baseline value (for example a different library, interface, or format reader for the same underlying data).
- The validation observation reports the same value for the same quantity as the baseline, so the independent paths agree.

排除条件：

- The second run repeats the identical code or access path, so agreement is not informative.
- The recomputed quantity, scope, or selection differs from the baseline.
- The two observations report different values, or no baseline value exists.
- The second observation only inspects the persisted output rather than recomputing the quantity.

### CONFIRMS_PERSISTED_OUTPUT_MATCHES_COMPUTED_VALUE

签名：`CONFIRMS_PERSISTED_OUTPUT_MATCHES_COMPUTED_VALUE(computed_result: observation, inspection_action: action, artifact_observation: observation)`

An action inspects the persisted output artifact, and its observation shows artifact content identical to a value the agent previously computed, confirming that the stored output faithfully reflects the computed result.

参数：

- `computed_result: observation`：The observation reporting the value produced by the computation.
- `inspection_action: action`：The action that reads, lists, or otherwise inspects the persisted output artifact.
- `artifact_observation: observation`：The observation showing the content of the persisted output artifact.

成立条件：

- The computed result observation reports a specific value produced by the agent's computation.
- The inspection action targets the file or artifact to which that value was written.
- The artifact observation shows content whose value is identical to the reported computed value, including any required formatting constraints.

排除条件：

- The artifact content is missing, empty, truncated, or differs from the computed value.
- The inspection action does not read or list the output artifact.
- No previously computed value exists to compare against.
- Agreement is only asserted in reasoning but is not visible in the artifact observation.

### CONCLUDES_WITH_FINAL_ANSWER

签名：`CONCLUDES_WITH_FINAL_ANSWER(conclusion_reasoning: reasoning)`

The reasoning presents the definitive final result of the task, connects it to the supporting evidence chain (and, where applicable, to the produced output artifact), and asserts that the task is complete.

参数：

- `conclusion_reasoning: reasoning`：The agent text presenting the final result together with its supporting justification and a completion claim.

成立条件：

- The reasoning presents a specific final value or result as the answer to the task.
- The reasoning links that result to identifiable supporting evidence, such as prior observations, and to any produced output artifact when one was required.
- The reasoning explicitly states that the task is complete or finished.

排除条件：

- The reasoning is intermediate, exploratory, or tentative about the result.
- No final value or result is stated.
- The reasoning only describes steps or plans without asserting completion.
- The stated result is presented only as a candidate still subject to further verification.

### ENUMERATES_COMPETING_EXPLANATIONS

签名：`ENUMERATES_COMPETING_EXPLANATIONS(reasoning: reasoning)`

The reasoning lays out two or more alternative explanations for the same observed situation, treating them as rival candidates whose truth is still to be determined before a course of action is chosen.

参数：

- `reasoning: reasoning`：The reasoning node enumerating the alternative explanations for the observed situation.

成立条件：

- At least two distinct candidate explanations are stated for the same observed condition.
- The alternatives are presented as competing, still-undetermined possibilities rather than as settled findings.

排除条件：

- Only a single explanation is offered.
- The enumerated items are steps of a plan, candidate solutions, or facts about the state rather than rival explanations for why the state is as observed.
- One explanation is already asserted as established, so no genuine competition between alternatives remains.

### ELIMINATES_EXPLANATION_WITH_CONTRARY_EVIDENCE

签名：`ELIMINATES_EXPLANATION_WITH_CONTRARY_EVIDENCE(reasoning: reasoning, observation: observation)`

The reasoning discards a candidate explanation for an observed situation because identifiable content of an observation contradicts a condition that the explanation requires.

参数：

- `reasoning: reasoning`：The reasoning node rejecting the candidate explanation.
- `observation: observation`：The observation whose content contradicts the rejected explanation.

成立条件：

- The reasoning names or clearly refers to a candidate explanation it discards.
- The reasoning cites identifiable observation content that conflicts with what that explanation would require, such as an empty listing contradicting a stash hypothesis or a clean status contradicting an uncommitted-changes hypothesis.

排除条件：

- The reasoning narrows possibilities without stating what rules a candidate out.
- The observation is compatible with the discarded explanation or unrelated to it.
- What is discarded is a candidate solution or artifact rather than an explanation for the observed situation.

### SELECTS_TARGET_AMONG_CANDIDATES

签名：`SELECTS_TARGET_AMONG_CANDIDATES(reasoning: reasoning, observation: observation)`

The reasoning identifies which of several comparable candidate items is the one relevant to the task, justifying the choice with discriminating attributes visible in an observation rather than by position, recency, or surface similarity.

参数：

- `reasoning: reasoning`：The reasoning node comparing the candidates and identifying the relevant one.
- `observation: observation`：The observation exposing the discriminating attributes of the candidates.

成立条件：

- At least two comparable candidate items are distinguished in the reasoning.
- The selection is justified by at least one discriminating attribute visible in the observation, such as provenance, authorship, timestamp, or creation context.
- The reasoning concludes that one candidate is the item relevant to the task.

排除条件：

- Only one candidate is considered, so no discrimination is needed.
- A candidate is chosen by position, recency, or guess without cited discriminating evidence.
- The cited discriminating attribute is not actually present in the observation.

### PREDICTS_OUTCOME_OF_PLANNED_OPERATION

签名：`PREDICTS_OUTCOME_OF_PLANNED_OPERATION(reasoning: reasoning, observation: observation)`

The reasoning forecasts a specific consequence of an operation it has not yet performed, deriving that forecast from identifiable state evidence reported in an observation.

参数：

- `reasoning: reasoning`：The reasoning node naming the planned operation and stating the predicted consequence.
- `observation: observation`：The observation supplying the state evidence on which the forecast rests.

成立条件：

- The reasoning names an operation that is planned but not yet performed.
- A specific expected consequence of that operation is stated, such as an anticipated conflict, failure, or produced change.
- The forecast is tied to identifiable state evidence in the observation.

排除条件：

- The reasoning describes an outcome that has already been observed.
- The forecast is speculation not connected to identifiable state evidence.
- No specific consequence is predicted.
- The observation content cited is unrelated to the predicted consequence.

### DIAGNOSES_ROOT_CAUSE

签名：`DIAGNOSES_ROOT_CAUSE(reasoning: reasoning)`

The reasoning reconstructs a causal account of how an observed state came to be, specifying the preceding events or actions responsible for it rather than merely restating what the state is.

参数：

- `reasoning: reasoning`：The reasoning node presenting the causal reconstruction of the observed state.

成立条件：

- The reasoning specifies one or more preceding events or actions, in sequence, as the cause of the observed condition.
- The account explains why the current state has the observed properties, not merely what those properties are.

排除条件：

- The reasoning only restates the reported problem or the observed state.
- The reasoning lists possible causes without committing to a causal account.
- The reasoning merely paraphrases observed output without identifying the preceding events that produced it.

### ESTABLISHES_CONFLICT_RESOLUTION_PRECEDENCE

签名：`ESTABLISHES_CONFLICT_RESOLUTION_PRECEDENCE(reasoning: reasoning, observation: observation)`

Given an observation showing that two versions of the same artifact conflict, the reasoning decides which version prevails and justifies that choice with a stated precedence rationale rather than an arbitrary pick.

参数：

- `reasoning: reasoning`：The reasoning node choosing the prevailing version and stating the precedence rationale.
- `observation: observation`：The observation exhibiting the conflicting versions of the artifact.

成立条件：

- The observation presents two conflicting alternatives for the same artifact.
- The reasoning selects one alternative as the resulting outcome.
- The reasoning states a rationale for why that alternative supersedes the other, such as which change is newer or which reflects the current situation.

排除条件：

- The reasoning only describes the conflict without selecting a side.
- A side is selected without any stated justification, or purely by position or convenience.
- The observation does not actually show conflicting alternatives for the same artifact.

### PLANS_POST_ACTION_VERIFICATION

签名：`PLANS_POST_ACTION_VERIFICATION(reasoning: reasoning)`

The reasoning explicitly plans one or more checks to be performed after an action in order to determine whether the action produced the required outcome or final state.

参数：

- `reasoning: reasoning`：The reasoning text specifying the future verification checks and their purpose.

成立条件：

- The reasoning refers to future verification or checking steps.
- The checks are directed at confirming the outcome or final state of a completed or planned action, rather than at initial exploration.
- At least one check criterion or target state is identifiable.

排除条件：

- The reasoning only describes exploratory inspection before any relevant action.
- The reasoning only reports checks already completed without planning future verification.
- The reasoning states a general next step without a validation purpose.

### RESOLVES_OBSERVED_CONFLICT_BY_SELECTING_VERSION

签名：`RESOLVES_OBSERVED_CONFLICT_BY_SELECTING_VERSION(conflict_observation: observation, resolution_reasoning: reasoning, resolution_action: action)`

An observation identifies competing alternative contents in a target artifact; the reasoning selects one alternative with an explicit justification; the action applies the selected alternative to resolve the conflict.

参数：

- `conflict_observation: observation`：The observation showing incompatible alternatives, conflict markers, or otherwise competing versions of the target content.
- `resolution_reasoning: reasoning`：The reasoning that selects one competing version and gives a justification for that selection.
- `resolution_action: action`：The action that applies the selected version or otherwise carries out the conflict resolution.

成立条件：

- The observation contains identifiable conflicting or competing content alternatives.
- The reasoning states which alternative is adopted and gives an identifiable semantic reason such as precedence, correctness, or supersession.
- The action implements that selected alternative, for example by adopting, staging, or committing that version.

排除条件：

- The observation does not contain an identifiable conflict or competing versions.
- The reasoning only notes the presence of a conflict without selecting a version.
- The action is unrelated to the selected version or applies a different resolution.
- No justification for the selection is provided.

### DERIVES_EXACTNESS_CONSTRAINT_FROM_MEASUREMENT

签名：`DERIVES_EXACTNESS_CONSTRAINT_FROM_MEASUREMENT(measurement_observation: observation, reasoning: reasoning)`

The reasoning extracts a precise measurable or formatting property from an observation and adopts preservation of that property as a requirement for a subsequent action or acceptance check.

参数：

- `measurement_observation: observation`：The observation reporting an exact quantitative or formatting property such as byte count, hash, whitespace pattern, or exact text layout.
- `reasoning: reasoning`：The reasoning that refers to the precise property as a requirement to be matched or preserved.

成立条件：

- The observation provides a precise measurable, byte-level, or formatting property.
- The reasoning explicitly refers to that property as something that must be matched or preserved.
- The property is used as a constraint on a subsequent action or as an acceptance criterion.

排除条件：

- The observation provides only qualitative or approximate information.
- The reasoning does not impose preservation or matching of the measured property.
- The measured property is mentioned but not used as a requirement or acceptance criterion.

### ACTION_RESULT_CONFIRMS_INTENDED_EFFECT

签名：`ACTION_RESULT_CONFIRMS_INTENDED_EFFECT(action: action, result_observation: observation)`

The observation reports a resulting state that confirms the action achieved its intended effect, rather than merely indicating that the action was invoked or completed.

参数：

- `action: action`：The action whose intended effect is being assessed.
- `result_observation: observation`：The observation reporting the resulting state after the action.

成立条件：

- The observation contains an outcome state that matches the action's intended effect.
- No error or contradictory state undermines that claimed effect.
- The effect is inferred from the reported state, not merely from an acknowledgment that the command was executed.

排除条件：

- The observation only shows that the action was invoked or completed without evidence of its effect.
- The observation reports an error, failure, or incomplete result for the intended effect.
- The observation is unrelated to the action's intended effect.

### LOCATES_TARGET_WITHIN_OBSERVED_STRUCTURE

签名：`LOCATES_TARGET_WITHIN_OBSERVED_STRUCTURE(reasoning: reasoning, observation: observation)`

The reasoning identifies a specific element within a structure, history, or set of records described by an observation as the location, container, or source of a target of interest.

参数：

- `reasoning: reasoning`：The reasoning node pinpointing a specific locus of the target within the observed structure.
- `observation: observation`：The observation describing the structure, history, or set of records being searched.

成立条件：

- The observation describes a structure, history, or set of records with identifiable individual elements.
- The reasoning points to at least one specific element within that observed structure as containing, retaining, or being associated with the target of interest.

排除条件：

- The reasoning only summarizes the observed structure without singling out any element.
- The reasoning states a target value without relating it to a location or record visible in the observation.
- The observation does not contain the structure or records being localized.

### PERSISTS_RECOVERED_VALUE_TO_OUTPUT

签名：`PERSISTS_RECOVERED_VALUE_TO_OUTPUT(action: action, reasoning: reasoning)`

An action writes a specific value that reasoning has identified as recovered or extracted information into the output artifact designated for it, so that the discovered value is preserved outside the search process.

参数：

- `action: action`：The action that writes or creates the designated output artifact.
- `reasoning: reasoning`：The reasoning identifying the recovered value and the output destination where it must be persisted.

成立条件：

- The reasoning identifies a specific value as recovered or extracted and indicates the output location where it should be persisted.
- The action writes that identified value to the indicated output artifact.

排除条件：

- The action writes unrelated, placeholder, or unverified content.
- The reasoning does not identify a recovered value or an output destination.
- The action only reads or inspects information without persisting it.

### APPLIES_REMEDIATION_TO_IDENTIFIED_ARTIFACT

签名：`APPLIES_REMEDIATION_TO_IDENTIFIED_ARTIFACT(action: action, reasoning: reasoning)`

An action performs a removal or elimination operation directed at an unwanted artifact, record, or retention mechanism that the reasoning has identified as the thing to be cleaned up.

参数：

- `action: action`：The action executing the cleanup or removal operation.
- `reasoning: reasoning`：The reasoning identifying the unwanted artifact, record, or retention mechanism and the removal strategy.

成立条件：

- The reasoning identifies a specific unwanted artifact, record, or mechanism that retains it.
- The reasoning indicates a strategy for removing or eliminating that target.
- The action executes an operation directed at that removal rather than at exploration or verification.

排除条件：

- The action is exploratory, diagnostic, or unrelated maintenance.
- The reasoning does not identify an unwanted artifact or retention mechanism.
- The action only checks whether removal is needed without performing removal.
- The action removes state merely for tidiness, with no identified unwanted target.

### APPLIES_STATED_CONSTRAINT_TO_DESIGN

签名：`APPLIES_STATED_CONSTRAINT_TO_DESIGN(reasoning: reasoning)`

The reasoning takes a specific requirement or constraint from the task specification and connects it to a concrete technical approach, configuration construct, parameter, or value, making identifiable how that choice realizes, satisfies, or violates the cited requirement.

参数：

- `reasoning: reasoning`：The reasoning text that connects a requirement stated in the task to a concrete approach, configuration choice, parameter, or value.

成立条件：

- The reasoning identifies a specific requirement or constraint stated by the task or requester.
- The reasoning selects or evaluates a concrete implementation choice, such as an approach, configuration construct, parameter, or value.
- The reasoning makes an identifiable link between the cited requirement and that choice, stating that the choice realizes, satisfies, or would violate the requirement.

排除条件：

- The reasoning only lists or restates requirements without connecting them to any concrete choice.
- The cited requirement plays no role in selecting or judging the choice.
- The choice is evaluated only on grounds unrelated to any stated requirement.
- The requirement has been converted into an abstract checkable admissibility condition with no concrete choice being selected or judged.

### SELECTS_APPROACH_FROM_CONSIDERED_ALTERNATIVES

签名：`SELECTS_APPROACH_FROM_CONSIDERED_ALTERNATIVES(reasoning: reasoning)`

The reasoning compares two or more alternative ways of achieving the same goal and commits to one of them with an articulated rationale for preferring it.

参数：

- `reasoning: reasoning`：The reasoning text comparing the candidate approaches and stating the chosen one with its rationale.

成立条件：

- At least two distinct candidate approaches are identified for the same goal.
- The reasoning states a comparison or trade-off between those approaches.
- The reasoning explicitly commits to one approach and gives a reason that favors it over the alternative.

排除条件：

- Only a single approach is described, with no alternative considered.
- Alternatives are mentioned but no selection among them is made.
- A chosen approach is restated without being compared against any alternative.
- The comparison rejects candidates purely because they violate hard requirements, leaving a single survivor with no trade-off weighed.

### RECOGNIZES_ANOMALY_IN_OBSERVATION

签名：`RECOGNIZES_ANOMALY_IN_OBSERVATION(reasoning: reasoning, observation: observation)`

The reasoning identifies a condition reported by an observation as unexpected, contradictory, or otherwise deviating from the anticipated state, and treats it as something requiring explanation, investigation, or handling because it bears on the intended outcome.

参数：

- `reasoning: reasoning`：The reasoning node that flags the reported condition as unexpected and states its significance.
- `observation: observation`：The observation reporting the warning, conflict, deviation, or otherwise unanticipated condition.

成立条件：

- The observation reports a warning, conflict, deviation, or unanticipated condition rather than the expected clean result.
- The reasoning characterizes that condition as unexpected, contradictory, or in need of investigation or handling.
- The reasoning indicates why the condition matters for the intended outcome.

排除条件：

- The observation matches the expected outcome and the reasoning treats it as ordinary success.
- The reasoning merely quotes the reported condition without judging it unexpected or consequential.
- The anomaly is explained with an identified benign origin and judged harmless to the required behavior.
- The deviation is only inferred later, without the reasoning connecting it to the observation.

### ADOPTS_PREEXISTING_CONFIGURATION_AS_INTENDED

签名：`ADOPTS_PREEXISTING_CONFIGURATION_AS_INTENDED(conforming_reasoning: reasoning, discovery_observation: observation)`

The reasoning treats a pre-existing configuration, artifact, or layout revealed by an observation as the environment's intended or authoritative design, and revises the plan so that the agent's own work conforms to or preserves it instead of overriding or duplicating it.

参数：

- `conforming_reasoning: reasoning`：The reasoning that characterizes the discovered artifact as intended or authoritative and revises the plan accordingly.
- `discovery_observation: observation`：The observation revealing the pre-existing configuration, layout, or artifact.

成立条件：

- The observation reveals a pre-existing configuration or artifact containing substantive settings, structure, or layout information.
- The reasoning explicitly characterizes that artifact as intended, pre-prepared, or authoritative for the environment.
- The reasoning changes planned actions so that the agent's own work conforms to or preserves the discovered artifact rather than replacing or duplicating it.

排除条件：

- The reasoning merely notes the artifact's existence without revising the plan.
- The discovered artifact is treated as incidental, defective, or as something to be replaced or overridden.
- No plan revision toward conformance with or preservation of the discovered artifact is expressed.

### INTERPRETS_ADVERSE_OBSERVATION_AS_BENIGN_OR_EXPECTED

签名：`INTERPRETS_ADVERSE_OBSERVATION_AS_BENIGN_OR_EXPECTED(result_reasoning: reasoning, negative_observation: observation)`

The reasoning interprets an observation that reports an error, missing content, residual artifact, unexpected entry, or other adverse or unexpected result as benign or expected, by explaining its cause or why it does not indicate a defect, and judges it not to impair required behavior or as consistent with correct progress.

参数：

- `result_reasoning: reasoning`：The reasoning explaining why the adverse or unexpected result is benign or expected at the current stage.
- `negative_observation: observation`：The observation containing the error response, missing content, residual artifact, unexpected entry, or other adverse or unexpected result being interpreted.

成立条件：

- The observation shows an error response, missing resource, empty content, residual artifact, unexpected entry, nonzero status, or other adverse or unexpected result.
- The reasoning explicitly explains why that result is expected, benign, or caused by a non-defect condition, such as a current intermediate stage, test instrumentation, or harmless residual state.
- The reasoning judges the result as not impairing required behavior or as consistent with correct progress, supported by or consistent with other evidence.

排除条件：

- The reasoning treats the adverse or unexpected result as a failure requiring correction.
- The reasoning ignores or merely repeats the result without interpreting it as benign or expected.
- The observation reports a positive or unambiguously successful result.
- The result is dismissed without any stated cause, or while contradicting evidence shows the required behavior is impaired.
- The error indication shows that a required output is missing or that the task cannot be completed as required.

### ASSESSES_ROBUSTNESS_ACROSS_HYPOTHETICAL_SCENARIOS

签名：`ASSESSES_ROBUSTNESS_ACROSS_HYPOTHETICAL_SCENARIOS(reasoning: reasoning)`

The reasoning considers two or more distinct hypothetical courses of behavior that an external actor, procedure, or environment might exhibit, and selects the candidate state, configuration, or action that remains valid or correct across all of the considered hypotheses.

参数：

- `reasoning: reasoning`：The agent text enumerating alternative hypothetical scenarios and comparing the validity of candidate states or actions across them.

成立条件：

- The reasoning describes at least two distinct hypothetical scenarios, procedures, or behaviors that an external actor or environment might follow.
- The reasoning evaluates which candidate state, configuration, or action remains valid under those enumerated scenarios.
- The reasoning selects or favors the candidate that survives the largest number of, and preferably all, the considered scenarios.

排除条件：

- The reasoning considers only a single expected scenario or line of behavior.
- The reasoning enumerates scenarios without drawing any comparative conclusion about which candidate state or action to adopt.
- The enumerated items are rival explanations for an already observed situation rather than hypothetical future behaviors.
- The candidate states differ only in incidental detail, so no robustness trade-off is actually weighed.

### ACKNOWLEDGES_RECURRING_OWN_ERROR

签名：`ACKNOWLEDGES_RECURRING_OWN_ERROR(reasoning: reasoning)`

The reasoning recognizes that a mistake made in the agent's own prior actions is a repeated or recurring pattern, and states a concrete corrective rule or commitment that the upcoming action is to follow.

参数：

- `reasoning: reasoning`：The agent text noting the repeated nature of its own mistake and stating the corrective rule it will follow.

成立条件：

- The reasoning identifies a mistake attributable to the agent's own prior action.
- The reasoning explicitly indicates that the mistake has recurred or is a recurring pattern rather than a one-off slip.
- The reasoning states a concrete corrective rule or commitment to be followed in the upcoming action.

排除条件：

- The reasoning describes a first-time mistake without indicating recurrence.
- The reasoning attributes the failure to the environment, tooling, or an external actor rather than to its own recurring behavior.
- The reasoning notes the mistake without committing to any corrective rule for the next action.

### COMPARES_MEASURED_VALUE_AGAINST_THRESHOLD

签名：`COMPARES_MEASURED_VALUE_AGAINST_THRESHOLD(reasoning: reasoning, observation: observation)`

The reasoning extracts a quantitative measurement reported in an observation and evaluates it against a stated limit, threshold, or required magnitude, asserting that the measured value satisfies or violates that requirement; the evaluation may also characterize the size or adequacy of the margin between the measurement and the threshold.

参数：

- `reasoning: reasoning`：The reasoning node that restates the reported measurement and evaluates it against the limit or requirement.
- `observation: observation`：The observation reporting the numeric measurement being evaluated.

成立条件：

- The observation contains a numeric value produced by a measurement, timing, or count.
- The reasoning explicitly relates that value to a stated limit, threshold, or required magnitude and asserts compliance or violation.

排除条件：

- The observation provides only qualitative information and no numeric comparison is made.
- The reasoning reports the numeric value without linking it to any limit or requirement.
- The reasoning compares quantities with each other without invoking a required limit or threshold.

### DISCARDS_EVIDENCE_FROM_FAILED_OPERATION

签名：`DISCARDS_EVIDENCE_FROM_FAILED_OPERATION(reasoning: reasoning, observation: observation)`

The reasoning judges a value or result recorded in an observation to be unusable or meaningless as evidence because the operation that produced it failed, thereby excluding that data from subsequent conclusions.

参数：

- `reasoning: reasoning`：The reasoning node explaining why the reported result is invalid evidence given the failure.
- `observation: observation`：The observation reporting both the failure of the underlying operation and the derived value or result in question.

成立条件：

- The observation indicates that the underlying operation failed or did not execute as intended.
- The observation also reports an accompanying measurement or result that would otherwise be informative.
- The reasoning explicitly states that the accompanying value or result is meaningless, invalid, or unusable because of that failure.

排除条件：

- The reasoning accepts or relies on the reported value as valid evidence.
- The observation shows no failure that would undermine the reported value.
- The reasoning notes the failure but says nothing about the validity of the accompanying value.

### IDENTIFIES_UNMITIGATED_RISK_AND_ACCEPTS

签名：`IDENTIFIES_UNMITIGATED_RISK_AND_ACCEPTS(reasoning: reasoning)`

The reasoning names a concrete residual failure scenario that the current setup does not guard against and explicitly decides not to mitigate it, judging the risk acceptable or the mitigation disproportionate.

参数：

- `reasoning: reasoning`：The reasoning node that raises the residual failure scenario and decides not to address it.

成立条件：

- The reasoning describes a specific, plausible failure scenario that remains possible under the current configuration.
- The reasoning explicitly concludes that no mitigation will be implemented, with a justification such as low likelihood, environmental stability, or disproportionate effort.

排除条件：

- The reasoning identifies a problem and proceeds to fix or mitigate it rather than accepting it.
- The reasoning contains only a general statement of confidence with no named residual failure scenario.
- The reasoning mentions a risk but leaves open whether it will be mitigated.

### LAUNCHES_PROCESS_ASYNCHRONOUSLY

签名：`LAUNCHES_PROCESS_ASYNCHRONOUSLY(launch_action: action)`

The action starts a long-running process in a detached or background mode so that control returns to the caller without waiting for the process to terminate.

参数：

- `launch_action: action`：The action that launches the process in a detached or background mode.

成立条件：

- The action explicitly detaches or backgrounds the launched process, using a background-job operator, a nohup-style detachment, or an equivalent asynchronous launch facility.
- The invocation is structured so that control returns immediately while the launched process keeps running.

排除条件：

- The action runs the process in the foreground and waits for it to terminate before returning.
- The action only registers the process to start later on an event or restart, without launching it now.
- No detachment, backgrounding, or asynchronous execution mechanism is present in the action.

### REVEALS_UNAVAILABLE_CAPABILITY

签名：`REVEALS_UNAVAILABLE_CAPABILITY(limitation_observation: observation)`

The observation itself reports that a command, tool, package, service, or other capability invoked by the agent is absent, not found, or otherwise unavailable, constraining the approach that can be used.

参数：

- `limitation_observation: observation`：The observation reporting the absent or unavailable command, tool, package, service, or capability.

成立条件：

- The observation explicitly indicates that a command, tool, package, service, or other capability is absent, not found, or otherwise unavailable.
- The unavailability is stated by the observation's own content rather than only inferred by the agent in separate reasoning.

排除条件：

- The observation reports a generic failure, such as invalid arguments or a non-zero exit status, without stating that a capability is absent or unavailable.
- The observation reports success or availability rather than absence.
- The reported absence concerns ordinary data content rather than a command, tool, or capability the agent attempted to use.

### RESOLVES_AMBIGUITY_BY_OBSERVED_BEHAVIOR

签名：`RESOLVES_AMBIGUITY_BY_OBSERVED_BEHAVIOR(reasoning: reasoning, observation: observation)`

The reasoning identifies an ambiguity or conflicting expectation about how a requirement, tool, or system will actually behave, and resolves it by treating the concrete behavior reported in an observation as the authoritative reference fact, adjusting its interpretation or plan to match that observed behavior.

参数：

- `reasoning: reasoning`：The agent text that names the ambiguity or conflicting expectation and adopts the observed behavior as authoritative.
- `observation: observation`：The observation reporting the concrete behavior that settles the ambiguity.

成立条件：

- The reasoning explicitly identifies a specific ambiguity, alternative reading, or conflict between expectations about how something will behave.
- The reasoning explicitly adopts the concrete outcome reported in the observation as the authoritative fact, rather than continuing to settle the matter by speculation.
- The reasoning adjusts its interpretation, decision, or plan to conform to that observed behavior.

排除条件：

- The reasoning merely uses the observation as general supporting evidence without any identified ambiguity or conflicting expectation.
- The observation does not concern the ambiguity in question.
- The ambiguity is resolved by an assumed or conventional interpretation rather than by deferring to observed behavior.
- The reasoning continues to speculate about the requirement or behavior instead of deferring to what was observed.

### VERIFIES_EFFECT_OF_PRIOR_ACTION

签名：`VERIFIES_EFFECT_OF_PRIOR_ACTION(modification_action: action, verification_action: action)`

A check action inspects observable state or behavior produced by an earlier state-changing action in order to establish whether that change actually took effect, independently of the earlier action's own reported result.

参数：

- `modification_action: action`：The earlier action that changes persistent or runtime state.
- `verification_action: action`：The later action that inspects the resulting state to confirm the effect of that change.

成立条件：

- The modification action changes state whose effect is independently observable, such as process status, logs, files, artifacts, or a listening endpoint.
- The verification action reads or queries that resulting state specifically to determine whether the modification action took effect, rather than performing the intended work itself.

排除条件：

- The verification action inspects state unrelated to the modification action.
- The verification action gathers information for an unrelated purpose rather than confirming the modification's effect.
- The two actions are merely adjacent in time without any inspection of the modification's effect.
- The verification action repeats the modification rather than inspecting the state it produced.

### VALIDATES_IMPLEMENTATION_WITH_EXECUTED_TEST

签名：`VALIDATES_IMPLEMENTATION_WITH_EXECUTED_TEST(test_authoring_action: action, test_execution_action: action, test_result_observation: observation)`

The agent authors an executable test or self-check that encodes explicit expected outcomes for a component's behavior, executes that authored test against the component, and the reported result is used to determine whether the component's behavior matches the expectations.

参数：

- `test_authoring_action: action`：The action that creates or writes the executable test or self-check, including assertions or expected values.
- `test_execution_action: action`：The action that runs the authored test against the component.
- `test_result_observation: observation`：The observation reporting the test's actual outputs, pass/fail status, or assertion results.

成立条件：

- The test authoring action produces an executable test or self-check containing at least one explicit expected outcome or assertion about behavior.
- The test execution action runs that authored test against the target component.
- The observation reports outcomes sufficient to determine whether the test passed or failed.

排除条件：

- The test is only written or inspected but never executed.
- The executed command is not the authored test or contains no behavioral assertions or expected outcomes.
- The observation is unrelated to the test or provides no pass/fail evidence.

### ASSESSES_REQUIREMENT_COMPLETION

签名：`ASSESSES_REQUIREMENT_COMPLETION(reasoning: reasoning)`

The reasoning evaluates the satisfaction status of multiple stated requirements or deliverables by explicitly mapping each to supporting evidence or an explicit satisfied/unsatisfied judgment, rather than issuing a single undifferentiated completion claim.

参数：

- `reasoning: reasoning`：The reasoning that enumerates requirements or deliverables and assesses their completion status.

成立条件：

- The reasoning identifies at least two distinct requirements or deliverables.
- For each identified requirement or deliverable, the reasoning states a satisfaction status, supporting evidence, or an explicit judgment of completion.

排除条件：

- The reasoning gives only a general completion claim without per-requirement assessment.
- The reasoning merely lists requirements without indicating whether each is satisfied.
- The reasoning evaluates only a single requirement without a multi-requirement assessment.

### IDENTIFIES_ERROR_PITFALL

签名：`IDENTIFIES_ERROR_PITFALL(reasoning: reasoning)`

The reasoning identifies a specific failure mode by which a plausible but naive approach would produce incorrect or misleading results in the current task, and indicates the safeguard or method that avoids that failure mode.

参数：

- `reasoning: reasoning`：The agent text diagnosing the potential failure mode and the mitigation.

成立条件：

- The reasoning names a concrete error-producing mechanism tied to the current data or task, such as a substring that would be counted twice or a boundary that would be miscounted.
- The reasoning states or implies how the chosen method avoids the identified failure mode.

排除条件：

- The reasoning offers only generic caution without naming a concrete failure mode.
- The failure mode is recognized only after an executed check has already revealed a discrepancy.
- The reasoning identifies a failure mode but does not connect it to the current data or task.

### RESOLVES_CONFLICTING_INFORMATION_SOURCES

签名：`RESOLVES_CONFLICTING_INFORMATION_SOURCES(reasoning: reasoning)`

The reasoning identifies a conflict between two pieces of information about the same entity that originate from different sources and selects one as authoritative with an identifiable justification.

参数：

- `reasoning: reasoning`：The agent text identifying the discrepancy and justifying the chosen source.

成立条件：

- The reasoning explicitly contrasts two different values or facts about the same entity, such as an environment-provided value versus an instruction-provided value.
- The reasoning selects one of them as authoritative and gives an identifiable reason for that selection.

排除条件：

- The reasoning uses a single consistent source without any conflict.
- The reasoning notes a discrepancy but leaves it unresolved or defers without justification.
- The conflicting information concerns different entities or unrelated facts rather than the same entity.

### VALIDATES_RESULT_AGAINST_EXPECTED_RELATIONS

签名：`VALIDATES_RESULT_AGAINST_EXPECTED_RELATIONS(reasoning: reasoning, observation: observation)`

The reasoning checks reported result values against structural relations that must hold among them given the definitions of the compared scopes or categories, and uses agreement or violation of those relations to judge the plausibility of the results.

参数：

- `reasoning: reasoning`：The agent text checking reported values against expected containment, monotonicity, or aggregation relations.
- `observation: observation`：The observation supplying the result values being checked.

成立条件：

- The observation reports numeric values for several related categories or scopes.
- The reasoning states a relationship that the values must satisfy given the scope definitions, such as nested-scope containment, monotonic ordering across widening periods, or sum equality with a grand total.
- The reasoning concludes that the values are consistent with, or violate, those relationships.

排除条件：

- The reasoning merely restates the reported values without invoking any expected relationship among them.
- The invoked relationship is not implied by the definitions of the compared scopes.
- The reasoning performs an independent recomputation instead of an internal consistency check.

### IDENTIFIES_CONFORMANCE_RISK

签名：`IDENTIFIES_CONFORMANCE_RISK(reasoning: reasoning)`

The reasoning anticipates that a produced artifact or result, despite substantively correct content, could be rejected, mismatch, or be judged nonconforming by an external validator, strict byte-level comparison, or acceptance requirement because of a specific representational or formatting property.

参数：

- `reasoning: reasoning`：The agent text identifying the specific property that could cause the artifact to fail external validation or strict comparison.

成立条件：

- The reasoning names a concrete representational or formatting property of the artifact or result, such as line-ending convention, byte layout, encoding, or exact text layout, that could cause nonconformance.
- The reasoning explains how that property could cause rejection or mismatch under external validation or strict comparison, even though the substantive content is correct.

排除条件：

- The reasoning states only a generic need for quality checking or double-checking without naming a specific conformance failure mode.
- The reasoning reports an observed defect in the artifact's substantive content rather than a risk of external rejection of a correct-content artifact.
- The reasoning only plans or performs a corrective action without assessing any acceptance risk.
- No external acceptance requirement, validator, or strict comparison is implicated.

### PRESERVES_VERIFIED_CONTENT_IN_FORMAT_REMEDIATION

签名：`PRESERVES_VERIFIED_CONTENT_IN_FORMAT_REMEDIATION(reasoning: reasoning, action: action)`

The action rewrites or reformats an artifact to change an incidental representational property while reproducing substantive content that the reasoning has already established as verified or correct.

参数：

- `reasoning: reasoning`：The agent text establishing that the substantive content is already verified or correct and that only a representational property needs correction.
- `action: action`：The artifact rewrite or reformat that changes the incidental representational property while preserving the verified content.

成立条件：

- The reasoning establishes that the substantive content or values of the artifact have already been verified or are correct, and that only an incidental representational property needs correction.
- The action rewrites or reformats the artifact, reproducing the same substantive content while changing that incidental representational property, such as line-ending convention, encoding, or layout.
- No substantive value is recomputed, added, or removed by the action.

排除条件：

- The action changes substantive values, or adds or removes data.
- The reasoning does not establish the content as already verified or correct before the rewrite.
- The action's purpose is to correct content rather than only an incidental representational property.

### ENFORCES_OUTPUT_SCOPE_CONSTRAINT

签名：`ENFORCES_OUTPUT_SCOPE_CONSTRAINT(reasoning: reasoning, action: action)`

The reasoning cites a constraint that limits which artifacts may remain or be created in the deliverable environment, and the action removes or avoids a non-permitted artifact in order to comply with that constraint.

参数：

- `reasoning: reasoning`：The agent text identifying the output-scope or file-permission constraint and connecting the removal or avoidance to compliance with it.
- `action: action`：The action that deletes, removes, or avoids a non-permitted artifact to satisfy the constraint.

成立条件：

- The reasoning cites an output-scope or file-permission constraint that limits which artifacts may remain or be created.
- The action removes a non-permitted artifact, or avoids creating or retaining one, in order to satisfy that constraint.
- The reasoning connects the removal or avoidance to compliance with the cited constraint.

排除条件：

- No output-scope or permission constraint is identified.
- The action is unrelated to which artifacts are permitted to remain.
- The action modifies or produces a permitted deliverable rather than removing or avoiding a non-permitted one.
- The artifact is removed only because it is no longer needed or for tidiness, with no scope constraint cited.

### DERIVES_GENERAL_RULE_FROM_EXAMPLES

签名：`DERIVES_GENERAL_RULE_FROM_EXAMPLES(reasoning: reasoning, example_observations: observation[])`

The reasoning infers a general input-to-output transformation rule from one or more observed input-output examples and extends that rule to cases beyond the exact observed examples.

参数：

- `reasoning: reasoning`：Agent text articulating the derived transformation rule and its generalization to unseen inputs.
- `example_observations: observation[]`：Observations that collectively supply the example input-output pairs from which the rule is inferred.

成立条件：

- The cited observations contain example input-output pairs.
- The reasoning articulates a rule, procedure, or invariant structure that reproduces the observed outputs from the observed inputs.
- The reasoning extends the rule beyond the exact observed pairs, for example by identifying parameters, invariant structure, or expected behavior on unseen inputs.
- The derived rule relies on identifiable content of the cited observations.

排除条件：

- The reasoning merely restates, copies, or summarizes the examples without deriving a rule.
- The reasoning proposes a rule that is unsupported by the example content.
- The reasoning describes a one-off operation rather than a generalizable transformation.
- The reasoning does not address how the derived rule applies beyond the observed examples.

### ATTEMPTS_PREREQUISITE_PROVISIONING

签名：`ATTEMPTS_PREREQUISITE_PROVISIONING(reasoning: reasoning, provisioning_action: action)`

The reasoning identifies a specific tool, package, component, or capability required by the task as absent or insufficient, and the action attempts to install, fetch, or otherwise provision that prerequisite, without implying that the attempt succeeded.

参数：

- `reasoning: reasoning`：Agent text identifying the missing or insufficient prerequisite and the intent to provision it.
- `provisioning_action: action`：The action attempting to install, fetch, or otherwise make the identified prerequisite available.

成立条件：

- The reasoning identifies a specific tool, package, component, or capability required by the task as missing, absent, or insufficient.
- The action attempts to install, fetch, or otherwise provision that specific prerequisite rather than performing the task's primary transformation.
- The predicate does not assert that the provisioning attempt succeeded.

排除条件：

- The action only uses an already available component.
- The action provisions a component without any identified deficiency.
- The action fetches task data rather than provisioning a required capability.
- The action is a pure query or verification step without a provisioning attempt.

### VERIFICATION_CONFIRMS_REQUIRED_STATE

签名：`VERIFICATION_CONFIRMS_REQUIRED_STATE(verification_action: action, verification_observation: observation)`

An action includes an explicit verification or validation step for a state required by the task, such as tool availability, version, or artifact integrity, and the observation reports a positive result confirming that required state.

参数：

- `verification_action: action`：The action containing the explicit check of the required state; it may also perform related work in the same invocation.
- `verification_observation: observation`：The observation reporting the check's result.

成立条件：

- The action explicitly includes a check of availability, version, integrity, or another required precondition.
- The observation reports a positive result confirming the required state, such as a resolved executable path and version string or a passing integrity verification.
- The confirmed state is required for the task rather than an incidental side effect.

排除条件：

- The observation reports a failure or continued absence, which instead supports failure diagnosis.
- The action merely produces task output whose correctness is not explicitly checked.
- The action contains no identifiable verification or validation step.
- The observation does not report a positive confirming result for the required state.

### EVALUATES_COMPETING_IMPLEMENTATIONS

签名：`EVALUATES_COMPETING_IMPLEMENTATIONS(reasoning: reasoning, variant_observations: observation[])`

The reasoning compares the content or behavior of two or more distinct candidate implementations, versions, or variants of an artifact, as exposed by observations, and reaches a comparative judgement about their relative correctness or suitability.

参数：

- `reasoning: reasoning`：The reasoning node contrasting the candidate implementations or versions.
- `variant_observations: observation[]`：The observations that collectively expose two or more distinct candidate implementations or versions of the artifact.

成立条件：

- The cited observations collectively expose at least two distinct implementations, versions, or variants of the same artifact or of artifacts serving the same role.
- The reasoning contrasts their structure, logic, or behavior using identifiable content of those observations.
- The reasoning reaches a comparative judgement about correctness or suitability, which may reject some or all of the variants rather than selecting one of them.

排除条件：

- Only one implementation or version is exposed, so no comparative evaluation is possible.
- The reasoning describes or summarizes the variants without making any comparative correctness or suitability judgement.
- The contrasted content is not drawn from the cited observations.
- The reasoning compares candidate approaches it has not yet realized as artifacts rather than existing implementations or versions.

### RESOLVES_CONFLICT_WITH_TARGETED_EDIT

签名：`RESOLVES_CONFLICT_WITH_TARGETED_EDIT(conflict_observation: observation, resolution_reasoning: reasoning, resolution_action: action)`

An observation reports unresolved conflicting content between competing versions or alternatives of an artifact, the reasoning determines how that conflict is to be resolved, and an action edits or overwrites the conflicted artifact so as to apply that resolution.

参数：

- `conflict_observation: observation`：The observation reporting the unresolved conflict between competing versions or alternatives of the artifact.
- `resolution_reasoning: reasoning`：The reasoning node determining how the conflict should be resolved, including any replacement content to be written.
- `resolution_action: action`：The action that edits or overwrites the conflicted artifact to apply the determined resolution.

成立条件：

- The conflict_observation explicitly reports unresolved conflict, such as conflict markers, a conflict status, or otherwise competing content for the same artifact.
- The resolution_reasoning specifies a resolution strategy or the replacement content to be written for the conflicted artifact.
- The resolution_action modifies or overwrites the conflicted artifact in accordance with that strategy.

排除条件：

- No unresolved conflict is reported by the conflict_observation.
- The resolution_action is unrelated to the conflicted artifact or applies a different resolution than the one specified.
- The conflict is only discussed or described, without any action applying a resolution.
- The reasoning merely notes that a conflict exists without determining how it should be resolved.

### DERIVES_VERSION_LINEAGE_FROM_METADATA

签名：`DERIVES_VERSION_LINEAGE_FROM_METADATA(lineage_reasoning: reasoning, metadata_observation: observation)`

The reasoning reconstructs ancestry or divergence relationships among artifact versions — such as a shared base and distinct descendant revisions — from version identifiers or reference metadata supplied by an observation.

参数：

- `lineage_reasoning: reasoning`：The reasoning node identifying a common base and/or divergent descendant versions from the reported identifiers.
- `metadata_observation: observation`：The observation supplying identifiers or references for multiple versions or revisions.

成立条件：

- The metadata_observation supplies identifiers or references for multiple versions or revisions.
- The lineage_reasoning identifies a shared base version and/or distinct descendant or divergent versions using those identifiers.

排除条件：

- The reasoning only repeats or lists identifiers without interpreting ancestry or divergence.
- The metadata_observation does not supply identifiers for multiple versions.
- No common ancestry or divergence relationship among versions is asserted.
- The reasoning compares versions for correctness or suitability without asserting how they are related by ancestry or divergence.

### CONSTRUCTS_GENERALIZATION_PROBE

签名：`CONSTRUCTS_GENERALIZATION_PROBE(probe_construction_action: action, generalization_reasoning: reasoning)`

The agent authors new test inputs or scenarios derived from a rule it inferred from limited examples, in order to check whether that rule holds on cases beyond the supplied reference examples rather than merely re-running them.

参数：

- `probe_construction_action: action`：The action that writes or assembles the additional, agent-generated test inputs or scenarios.
- `generalization_reasoning: reasoning`：Agent text stating or presupposing the inferred rule and the intent to test whether it generalizes to unseen inputs.

成立条件：

- The reasoning states or presupposes a rule, pattern, or transformation inferred from the available examples.
- The action authors new inputs or scenarios that go beyond the supplied examples and are constructed from that inferred rule, for example by generating instances parameterized by the rule.
- The purpose of the constructed inputs is to test whether the rule holds on cases not covered by the supplied examples.

排除条件：

- The action only re-runs or compares against the supplied reference examples without generating new inputs.
- The generated input is not derived from any rule inferred from the available examples.
- No inferred rule or generalization concern is expressed in the reasoning.
- The action merely inspects or displays the implementation without constructing new test material.

### DISAMBIGUATES_COMPETING_INTERPRETATIONS

签名：`DISAMBIGUATES_COMPETING_INTERPRETATIONS(reasoning: reasoning)`

The reasoning identifies two or more candidate interpretations or hypotheses that could account for the same available evidence and argues for one of them by citing a distinguishing consideration that separates the preferred candidate from its rivals.

参数：

- `reasoning: reasoning`：Agent text weighing at least two candidate interpretations of the same evidence and arguing for one of them.

成立条件：

- The reasoning names or clearly describes at least two alternative interpretations that could account for the same observed evidence.
- The reasoning supplies a distinguishing consideration, such as coverage of the data, internal consistency, or incompatibility of a rival with the evidence, that separates the preferred interpretation from the alternatives.
- The reasoning adopts one interpretation as preferred on the basis of that distinguishing consideration.

排除条件：

- The reasoning asserts a single interpretation without acknowledging a competing one.
- The reasoning lists alternatives but makes no attempt to distinguish or select among them.
- The alternatives are candidate solution approaches or course-of-action options rather than competing interpretations of the same evidence.
- The alternatives concern different evidence or different scopes, so they are not rivals accounting for the same data.
- No preferred interpretation is identified.

### REVISES_ARTIFACT_TO_AVOID_CONSTRAINT_VIOLATION

签名：`REVISES_ARTIFACT_TO_AVOID_CONSTRAINT_VIOLATION(reasoning: reasoning, revision_action: action)`

The reasoning identifies specific content of an existing or planned artifact as risking violation of an explicitly stated output, format, or interface constraint, and the associated action produces or attempts revised artifact content in which the flagged element is removed or altered.

参数：

- `reasoning: reasoning`：The agent text identifying the explicit constraint, the specific artifact element that risks violating it, and the change to be made.
- `revision_action: action`：The action that writes the revised artifact content without the flagged element.

成立条件：

- The reasoning refers to an explicit output, format, or interface constraint, such as a required exact output content or format.
- The reasoning identifies a specific element of the artifact that risks violating that constraint and indicates why it is a violation risk.
- The revision action produces or attempts to produce artifact content in which that flagged element is removed or altered.

排除条件：

- The artifact is revised for a functional bug, an added feature, or a stylistic preference without reference to a stated constraint risk.
- The action does not rewrite the artifact content.
- The reasoning discusses a constraint but identifies no specific artifact element as risking its violation.
- The reasoning merely restates the constraint without committing to a content change.

### CONFIRMS_OUTCOME_AGAINST_PREDICTION

签名：`CONFIRMS_OUTCOME_AGAINST_PREDICTION(prediction_reasoning: reasoning, outcome_observation: observation, confirmation_reasoning: reasoning)`

A reasoning node formulates an expected result before the corresponding execution outcome is observed, the observation reports the actual outcome, and a later reasoning node explicitly compares the actual outcome with the previously stated expectation and states whether they agree.

参数：

- `prediction_reasoning: reasoning`：The reasoning node stating the expected result before the outcome is observed.
- `outcome_observation: observation`：The observation reporting the actual execution outcome.
- `confirmation_reasoning: reasoning`：The reasoning node comparing the actual outcome with the previously stated expectation and stating agreement or disagreement.

成立条件：

- The prediction reasoning states at least one expected value or result derived independently of the execution being predicted, before that execution's outcome is observed.
- The outcome observation reports the actual result produced by the execution.
- The confirmation reasoning explicitly compares the actual outcome to the previously stated expectation and states agreement or disagreement.

排除条件：

- No expectation is stated before the outcome is observed.
- The confirmation reasoning restates the observed result without comparing it to a previously stated expectation.
- The expected result and the observed outcome are not comparable quantities.
- The expectation is only formulated after seeing the outcome, so it cannot serve as an advance prediction.

### IDENTIFIES_SPECIFICATION_AMBIGUITY

签名：`IDENTIFIES_SPECIFICATION_AMBIGUITY(reasoning: reasoning)`

The reasoning explicitly flags that a requirement, specification, or instruction admits multiple interpretations or lacks sufficient detail for a unique action.

参数：

- `reasoning: reasoning`：The agent text identifying the ambiguous requirement, field, rule, or instruction.

成立条件：

- The reasoning names a specific requirement, field, rule, or instruction that is ambiguous, underspecified, or open to multiple readings.
- The reasoning signals uncertainty or the existence of competing possible interpretations.

排除条件：

- The reasoning merely restates requirements without acknowledging any ambiguity.
- The reasoning makes a choice without noting that an ambiguity or interpretation issue exists.

### SYNTHESIZES_OBSERVATIONS_INTO_UNIFIED_MODEL

签名：`SYNTHESIZES_OBSERVATIONS_INTO_UNIFIED_MODEL(reasoning: reasoning, observations: observation[])`

The reasoning integrates content from multiple distinct observations into a single combined representation or understanding rather than treating them independently.

参数：

- `reasoning: reasoning`：The agent text combining information from multiple observations.
- `observations: observation[]`：The observations whose contents are integrated into the combined representation.

成立条件：

- The reasoning references or restates content from at least two distinct observations.
- The reasoning produces a unified model, state, schema, summary, or combined representation that integrates the observed information.
- The reasoning cross-references information across the observations rather than only listing them separately.

排除条件：

- The reasoning references only one observation.
- The reasoning lists observations independently without deriving any combined representation.
- No integrated understanding or combined model is stated.

### DERIVES_UNIFIED_SCHEMA_MAPPING_FROM_OBSERVATIONS

签名：`DERIVES_UNIFIED_SCHEMA_MAPPING_FROM_OBSERVATIONS(reasoning: reasoning, observations: observation[])`

The reasoning specifies correspondences between differently named fields, attributes, or schema elements observed in multiple sources and a common target schema or unified representation.

参数：

- `reasoning: reasoning`：The agent text defining field, attribute, or schema correspondences between observed sources and a unified representation.
- `observations: observation[]`：The observations exposing the source schemas, field names, or structural information used to derive the mapping.

成立条件：

- The reasoning identifies at least two differently named source fields, attributes, or schema elements as equivalent to one target field or schema element.
- The mapping is based on source structures, field names, or schema information exposed by the observations.
- The reasoning addresses correspondences across multiple observed source schemas or representations.

排除条件：

- The reasoning only repeats field names from a single source without cross-source correspondence.
- No equivalence between differently named fields or schema elements is stated.
- The mapping is unrelated to the observed source structures.

### VERIFIES_OUTPUT_AGAINST_STATED_REQUIREMENTS

签名：`VERIFIES_OUTPUT_AGAINST_STATED_REQUIREMENTS(validation_action: action, criteria_reasoning: reasoning, validation_observation: observation)`

A validation action tests produced outputs against requirements or expected properties explicitly stated in reasoning, and its result observation reports evidence about whether those checks passed.

参数：

- `validation_action: action`：The tool invocation that executes checks, assertions, or comparisons against the produced outputs.
- `criteria_reasoning: reasoning`：The agent text stating the requirements or expected properties to validate.
- `validation_observation: observation`：The observation reporting the check results or observed values relevant to the stated criteria.

成立条件：

- The criteria reasoning states specific requirements, properties, or expected values to be checked.
- The validation action executes assertions, inspections, or comparisons targeting those requirements.
- The validation observation reports pass/fail status or observed values that address the stated criteria.

排除条件：

- The action generates output rather than checking it against criteria.
- The observation merely displays output without comparison to stated requirements.
- No explicit validation criteria are stated in the reasoning.

### VERIFIES_DEPLOYED_SERVICE_WITH_REQUEST

签名：`VERIFIES_DEPLOYED_SERVICE_WITH_REQUEST(verification_reasoning: reasoning, request_action: action, response_observation: observation)`

After a service or component has been brought up, the reasoning identifies a specific behavior or requirement of the running service to verify, an action exercises the live service through its exposed interface, and the resulting observation reports a response that can be judged against the expected behavior.

参数：

- `verification_reasoning: reasoning`：Agent text identifying the deployed/running service behavior, endpoint, or requirement that is to be verified.
- `request_action: action`：The action that exercises the running service through its exposed interface, such as sending a request to its endpoint.
- `response_observation: observation`：The observation containing the service's response content, status, or other output relevant to the verification goal.

成立条件：

- The verification_reasoning identifies a specific behavior, endpoint, or requirement of a service that has been deployed or started and now must be confirmed.
- The request_action targets that running service through its exposed interface rather than merely reading configuration, files, or process status.
- The response_observation reports response content, status, or other output that can be compared with the expected behavior stated or implied by the verification goal.

排除条件：

- The service has not been started or deployed at the time the request is made.
- The action only inspects process state, files, logs, or configuration instead of exercising the running service interface.
- The request_action is unrelated to the stated verification goal.
- The observation reports only a transport failure or no interpretable service response.
- No verification goal or expected behavior is stated or implied in the reasoning.

### EXPLAINS_ANOMALOUS_RESULT_WITH_CAUSAL_HYPOTHESIS

签名：`EXPLAINS_ANOMALOUS_RESULT_WITH_CAUSAL_HYPOTHESIS(reasoning: reasoning, observation: observation)`

The reasoning accounts for an observation whose reported outcome deviates from what the agent anticipated by identifying a causal or mechanistic process that would produce that outcome, instead of merely noting or restating the deviation.

参数：

- `reasoning: reasoning`：The agent text constructing the causal or mechanistic explanation for the unexpected result.
- `observation: observation`：The tool result whose reported outcome deviates from what the agent anticipated.

成立条件：

- The observation reports an outcome that differs from the outcome the agent anticipated, for example uniform successes where rejections were expected, an unexpected quantity or timing, or a result that contradicts an assumed behavior.
- The reasoning identifies a concrete mechanism or process (such as pacing, serialization, request queueing/delay, per-invocation overhead, or an ignored or absent capability) that would produce exactly that deviation.
- The reasoning presents that mechanism as the reason this specific observed outcome occurred, rather than as an unrelated general remark or as a restatement of the output.

排除条件：

- The observation matches the expectation, so no deviation needs explaining.
- The reasoning only repeats the observed result, or expresses surprise, without proposing any mechanism.
- The proposed mechanism is incompatible with the content of the observation.
- The observation reports an outright error and the reasoning merely repeats or paraphrases the error text without explaining the causal process.

### ADAPTS_PROBE_TO_ELIMINATE_IDENTIFIED_CONFOUND

签名：`ADAPTS_PROBE_TO_ELIMINATE_IDENTIFIED_CONFOUND(reasoning: reasoning, adapted_action: action)`

The reasoning identifies a specific property of a previously used measurement, verification, or comparison technique—including a flawed reference value, baseline, or probing method—that distorted or constrained the result it produced, and the following action changes that technique or reference in exactly that respect so that a valid measurement or comparison of the same quantity becomes possible.

参数：

- `reasoning: reasoning`：The agent text identifying the confound or limitation in the earlier measurement, verification, or comparison technique and prescribing the adjusted technique or reference.
- `adapted_action: action`：The tool invocation that performs the same measurement or comparison with the adjusted technique or reference.

成立条件：

- The reasoning names a specific property of the earlier technique or reference (for example per-invocation startup delay spreading requests apart, sequential rather than concurrent execution, an unsupported option, a lower-precision reference, or an inappropriate scale or summation order) that distorted or invalidated the result obtained with it.
- The adapted action differs from the earlier technique or reference in exactly the respect the reasoning identified, so the identified confound no longer applies.
- The reasoning presents the adjustment as the means of obtaining a valid measurement or comparison of the same quantity, not as an unrelated new objective.

排除条件：

- The action repeats the same technique or reference without addressing the identified confound.
- The reasoning provides no identifiable flaw or limitation in the previous approach, so no confound is being eliminated.
- The technique is changed only for convenience or to satisfy an unrelated requirement rather than for measurement or comparison validity.
- The earlier attempt yielded no interpretable information because the method or tool was unavailable or unparseable; recovering from an unusable check is a distinct mechanism.

### RESOLVES_INSTRUCTION_CONFLICT

签名：`RESOLVES_INSTRUCTION_CONFLICT(conflict_reasoning: reasoning)`

The reasoning recognizes that two applicable instructions, rules, or requirements pull in conflicting directions for the current step, and explicitly justifies how the tension is settled, for example by prioritizing one, interpreting their scopes so they do not overlap, or choosing a reading that keeps both acceptable.

参数：

- `conflict_reasoning: reasoning`：The reasoning node that names the competing instructions or constraints and states how the conflict is resolved.

成立条件：

- The reasoning identifies at least two instructions, constraints, or requirements that are both applicable to the current action and are in tension or conflict.
- The reasoning explicitly states a resolution of that tension, such as a prioritization, a scope interpretation that removes the overlap, or a compromise reading that keeps both compatible.

排除条件：

- The reasoning follows an instruction or constraint without acknowledging any competing instruction or requirement.
- The reasoning acknowledges a tension or contradiction but leaves it unresolved and proceeds without justification.
- The competing considerations are not both applicable to the action being performed.
- The reasoning resolves a conflict between two versions or facts about an artifact or value rather than between applicable instructions or requirements.

### DECLINES_OPTIONAL_CHANGE_FOR_REQUIREMENT_FIDELITY

签名：`DECLINES_OPTIONAL_CHANGE_FOR_REQUIREMENT_FIDELITY(fidelity_reasoning: reasoning)`

The reasoning weighs an optional enhancement, extra field, or deviation that is not demanded by the stated requirements, and explicitly decides against it in order to stay faithful to what was actually asked, avoiding scope creep or unintended departure from the specification.

参数：

- `fidelity_reasoning: reasoning`：The reasoning node that considers an optional enhancement or deviation and explicitly rejects it to preserve fidelity to the stated requirements.

成立条件：

- The reasoning identifies a concrete optional enhancement, additional element, or alternative that is not required by the stated requirements.
- The reasoning explicitly states that the option is unnecessary, unrequested, or could conflict with the stated requirements.
- The reasoning explicitly decides not to apply the optional change.

排除条件：

- The reasoning simply never considers the optional change, so nothing is weighed and rejected.
- The reasoning adopts the optional enhancement rather than declining it.
- The optional change is rejected for a reason unrelated to fidelity to the stated requirements, such as performance or convenience.
- The reasoning decides against an approach because a technical constraint or unavailable capability blocks it rather than because the change would exceed the requirements.

### DECLARES_TASK_COMPLETION

签名：`DECLARES_TASK_COMPLETION(reasoning: reasoning)`

The reasoning asserts that the task as a whole is complete, with its stated requirements or deliverables satisfied and verified, rather than reporting only a single intermediate check, an individual deliverable, or remaining work.

参数：

- `reasoning: reasoning`：The reasoning node that declares overall completion of the task and its requirements or deliverables.

成立条件：

- The reasoning explicitly states that the task, or all of its stated requirements or deliverables, is complete, finished, satisfied, or verified.
- The completion assertion covers the task as a whole rather than a single intermediate check, probe, or partial step.

排除条件：

- The reasoning only plans future work or reports partial progress with remaining work outstanding.
- The reasoning reports a single check result or the status of a single deliverable without concluding that the overall task is complete.
- The reasoning presents one final value for a single-question task together with its supporting evidence chain, without making an aggregate completion claim about multiple requirements or deliverables.
- The reasoning's own content acknowledges that a required item remains unverified, failing, or undone, contradicting the completion claim.

### PROPOSES_TESTABLE_HYPOTHESIS

签名：`PROPOSES_TESTABLE_HYPOTHESIS(reasoning: reasoning)`

The reasoning offers a specific but provisional explanation, interpretation, or assumption about an artifact, system state, or cause that is presented as uncertain and can be checked by further observation or action.

参数：

- `reasoning: reasoning`：The reasoning node containing the provisional explanation or assumption.

成立条件：

- The reasoning identifies a specific candidate explanation or interpretation, such as what an artifact might be, why a result occurred, or where a target may reside.
- The explanation is presented with uncertainty or as something needing verification rather than as an already established fact.

排除条件：

- The reasoning states only a confirmed conclusion, or repeats an observation without proposing any explanation.
- The reasoning contains only a plan of action with no candidate explanation or assumption to test.
- The proposed idea is too vague to be checked by any identifiable subsequent observation or action.

### GUIDES_NEXT_INVESTIGATION_BY_OBSERVED_FEATURE

签名：`GUIDES_NEXT_INVESTIGATION_BY_OBSERVED_FEATURE(observation: observation, reasoning: reasoning)`

The reasoning uses a specific feature reported in an observation as the basis for selecting the next investigative target or action.

参数：

- `observation: observation`：The observation reporting a feature, artifact, directory, file listing, size, or result that can motivate further investigation.
- `reasoning: reasoning`：The reasoning node that references the observed feature and formulates the next investigative step from it.

成立条件：

- The observation reports an identifiable feature, such as a discovered directory, file, size, content pattern, or occurrence.
- The reasoning explicitly refers to or relies on that feature when selecting what to investigate or do next.
- The next investigative step is connected to the observed feature rather than being unrelated background activity.

排除条件：

- The reasoning merely repeats the observation without deriving or selecting a next investigative step.
- The next step is unrelated to any feature reported in the observation.
- The observation contains no identifiable feature that the reasoning uses for guidance.
- The reasoning plans a next step from prior knowledge or a general obligation without citing any feature of the observation.

### DISMISSES_CANDIDATE_AS_UNINFORMATIVE

签名：`DISMISSES_CANDIDATE_AS_UNINFORMATIVE(dismissal_reasoning: reasoning, content_observation: observation)`

The reasoning rejects or deprioritizes an inspected artifact or information source as a source of useful information because its observed content appears placeholder, random, unreadable, or otherwise uninformative.

参数：

- `dismissal_reasoning: reasoning`：The reasoning node explicitly characterizing the candidate as uninformative or deprioritizing it.
- `content_observation: observation`：The observation showing the candidate's content or metadata that makes it appear uninformative.

成立条件：

- The observation shows content that can reasonably be judged dummy, random, unreadable, or otherwise lacking useful information.
- The reasoning explicitly characterizes that candidate as a dummy, random data, noise, or otherwise not useful, or deprioritizes it in favor of another candidate.

排除条件：

- The reasoning merely notes uncertainty or unusual content while continuing to treat the same candidate as a primary source for the same kind of information.
- The reasoning reinterprets the same content as a useful artifact of a different type rather than dismissing the candidate.
- The observation contains no content or metadata supporting the dismissal.
- The reasoning does not actually reject or deprioritize the candidate.

### INFERS_RESOURCE_TYPE_OR_STRUCTURAL_ROLE_FROM_CONTENT

签名：`INFERS_RESOURCE_TYPE_OR_STRUCTURAL_ROLE_FROM_CONTENT(interpretation_reasoning: reasoning, content_observation: observation)`

The reasoning interprets observable content evidence — a byte pattern, embedded string, occurrence pattern, size or metadata signature, or internal structure — as indicating that a resource has a particular type, format, or internal structural role.

参数：

- `interpretation_reasoning: reasoning`：The reasoning node stating the inferred resource type, format, or structural role.
- `content_observation: observation`：The observation containing the content pattern, embedded artifact, occurrence evidence, or metadata used for the inference.

成立条件：

- The observation contains a recognizable content pattern, embedded artifact, occurrence pattern, size or metadata signature, or other structural evidence.
- The reasoning states a specific type, format, or structural role for the resource that is supported by that observed evidence.
- The inference goes beyond merely reporting the raw content by assigning the resource an interpretable nature or role.

排除条件：

- The reasoning only reports the raw bytes or raw content without making a type or structural-role inference.
- The inferred resource type or role is unsupported by any identifiable feature in the observation.
- The observation is unrelated to the stated resource type or structural interpretation.
- The reasoning merely dismisses the content as noise or filler without assigning it a type, format, or structural role.

### ASSESSES_CANDIDATE_AGAINST_CONSTRAINTS

签名：`ASSESSES_CANDIDATE_AGAINST_CONSTRAINTS(assessment_reasoning: reasoning, candidate_evidence: observation)`

The reasoning considers an identifiable candidate value, fragment, or occurrence supplied by observed content and evaluates whether it satisfies one or more explicitly stated requirements, reaching a judgment of compliance, partial compliance, or violation; the candidate may be a value assembled from multiple observed fragments, and the judgment may draw on the candidate's observed surrounding context.

参数：

- `assessment_reasoning: reasoning`：The reasoning that evaluates the candidate against the stated requirements.
- `candidate_evidence: observation`：The observation containing the candidate value, an observed fragment of it, or the surrounding context from which the candidate is extracted or assembled.

成立条件：

- The observation contains an identifiable candidate value, fragment, or occurrence, or content from which the candidate is assembled.
- The assessment_reasoning refers to at least one explicit requirement and compares the candidate to it.
- The reasoning reaches a conclusion about compliance, partial compliance, or noncompliance; noncompliance may include rejecting a spurious occurrence because its observed adjacent context violates the required format or character set.

排除条件：

- The reasoning only extracts or repeats the candidate without evaluating requirements.
- No explicit requirement is applied to the candidate.
- The observation does not contain the candidate or the context used to assess it.
- The reasoning evaluates a requirement or deliverable independently of any candidate value.

### VERIFIES_CANDIDATE_BY_TARGETED_REEXTRACTION

签名：`VERIFIES_CANDIDATE_BY_TARGETED_REEXTRACTION(verification_reasoning: reasoning, extraction_action: action, extraction_result: observation)`

A proposed candidate or candidate fragment is checked by re-reading the exact stored location, offset, or field from which it was claimed to originate, and the returned data are compared with the candidate to confirm or refute it.

参数：

- `verification_reasoning: reasoning`：The reasoning selecting the candidate and the exact location or field to re-read.
- `extraction_action: action`：The action that retrieves data from the identified location.
- `extraction_result: observation`：The observation reporting the retrieved data for comparison with the candidate.

成立条件：

- The verification_reasoning identifies a candidate or fragment and a specific location, offset, or field to inspect.
- The extraction_action retrieves data from that identified location rather than performing an untargeted search.
- The extraction_result contains data that can be directly compared with the candidate, confirming or refuting it.

排除条件：

- The action is an untargeted exploration not tied to a proposed candidate.
- The retrieved data cannot be compared with the candidate.
- The reasoning does not identify what is being verified or where it should be found.
- The action independently recomputes the candidate through a different path rather than re-reading the claimed source location.

### EXCLUDES_ALTERNATIVE_CANDIDATES_BY_EXHAUSTIVE_SEARCH

签名：`EXCLUDES_ALTERNATIVE_CANDIDATES_BY_EXHAUSTIVE_SEARCH(exclusion_reasoning: reasoning, exhaustive_search_action: action, search_result: observation)`

Reasoning establishes that a candidate is unique, or that no competing candidate satisfies the relevant criterion, by directing an exhaustive search over the available artifact or corpus and interpreting the search result as excluding alternatives.

参数：

- `exclusion_reasoning: reasoning`：The reasoning that seeks to rule out competing candidates or confirm uniqueness.
- `exhaustive_search_action: action`：The action that enumerates occurrences of a relevant pattern or feature across the available artifact or corpus.
- `search_result: observation`：The observation listing the occurrences found by the search.

成立条件：

- The exclusion_reasoning identifies a need to rule out alternatives or confirm that a candidate is the only qualifying occurrence.
- The exhaustive_search_action searches the relevant artifact or corpus for a pattern or feature rather than checking a single known location.
- The search_result shows that no additional qualifying candidate was found, or that the only qualifying hit is the known candidate, and the reasoning uses this to exclude alternatives.

排除条件：

- The search is limited to a single known location and cannot reveal alternatives.
- The observation reports additional qualifying candidates that are not excluded.
- The search result is not interpreted as relevant to uniqueness or alternative exclusion.
- The reasoning searches for additional context about one already identified match rather than attempting to enumerate competing candidates across the artifact.

### CORROBORATES_CANDIDATE_WITH_INDEPENDENT_METADATA

签名：`CORROBORATES_CANDIDATE_WITH_INDEPENDENT_METADATA(corroboration_reasoning: reasoning, metadata_observation: observation)`

Reasoning uses a separately recorded metadata value, such as a length, size, count, or structural field, that is independent of a proposed candidate's own expression to check the candidate's consistency and thereby corroborate or undermine it.

参数：

- `corroboration_reasoning: reasoning`：The reasoning that compares the candidate with the independent metadata value.
- `metadata_observation: observation`：The observation containing the metadata value used for the consistency check.

成立条件：

- The metadata_observation contains a value that is independent of the candidate's own expression, such as a stored length, size, count, or structural field.
- The corroboration_reasoning compares the candidate or its expected properties with that metadata value.
- The comparison yields a consistency result that the reasoning uses to corroborate or undermine the candidate.

排除条件：

- The metadata is merely the candidate itself or a direct repetition of it.
- The reasoning mentions metadata without comparing it to the candidate.
- No consistency conclusion is drawn from the metadata.
- The metadata is used to generate a new requirement for an action rather than to check an already proposed candidate.

### RECONSTRUCTS_CANDIDATE_FROM_COMPLEMENTARY_FRAGMENTS

签名：`RECONSTRUCTS_CANDIDATE_FROM_COMPLEMENTARY_FRAGMENTS(reasoning: reasoning)`

The reasoning treats two or more partial segments as complementary parts of a single result, combines them into one candidate, and evaluates the combined candidate against at least one whole-candidate constraint such as total length, boundary pattern, allowed character set, or checksum.

参数：

- `reasoning: reasoning`：The reasoning node that identifies the complementary segments, combines them into one candidate, and checks the combined candidate.

成立条件：

- The reasoning identifies at least two partial segments that are treated as complementary parts of the same result rather than as separate results.
- The reasoning combines the segments into a single candidate result.
- The reasoning evaluates the combined candidate against at least one whole-candidate constraint, such as total length, prefix, suffix, allowed character set, or checksum.

排除条件：

- The reasoning deals with only one segment or does not combine segments.
- The reasoning combines segments but does not evaluate the combined candidate against any whole-candidate constraint.
- The segments are not presented as parts of the same candidate result.
- The reasoning merely restates a combined value without any constraint evaluation.

### FORMULATES_IMPLEMENTATION_DESIGN

签名：`FORMULATES_IMPLEMENTATION_DESIGN(design_reasoning: reasoning)`

The reasoning constructs a concrete candidate implementation design, specifying artifact structure, algorithmic components, or syntax/mechanism choices intended to satisfy stated requirements.

参数：

- `design_reasoning: reasoning`：Reasoning that specifies the intended structure, algorithm, or mechanism of a proposed solution.

成立条件：

- The reasoning specifies a concrete solution structure, algorithm, artifact organization, or syntax/mechanism choice rather than only restating a goal.
- The reasoning indicates how at least one specified component or mechanism is expected to contribute to satisfying a stated requirement.

排除条件：

- The reasoning only states that an implementation, inspection, or test will be performed without describing the proposed design.
- The reasoning only evaluates observed results without proposing or constructing a design.
- The reasoning only enumerates requirements or constraints without describing a concrete implementation structure.

### VERIFIES_MULTI_INTERFACE_COMPATIBILITY

签名：`VERIFIES_MULTI_INTERFACE_COMPATIBILITY(verification_reasoning: reasoning, execution_action: action, result_observation: observation)`

The reasoning sets an acceptance requirement that an artifact must operate through multiple specified invocation interfaces or execution paths, the action exercises those paths, and the observation reports successful or equivalent outcomes from them.

参数：

- `verification_reasoning: reasoning`：Reasoning identifying the multiple interfaces or execution paths that must succeed.
- `execution_action: action`：Action exercising the artifact through those interfaces or paths.
- `result_observation: observation`：Observation reporting outcomes from the exercised paths.

成立条件：

- The reasoning identifies at least two specified invocation interfaces or execution paths that the artifact must satisfy.
- The action exercises the artifact through each of those identified paths, optionally across multiple inputs.
- The observation reports outcomes from those paths that can be compared for correctness or equivalence and that demonstrate successful operation.

排除条件：

- Only one invocation interface or execution path is exercised.
- The action only compiles the artifact or checks syntax without executing the required paths.
- The observation does not report outcomes for the paths being compared.
- At least one required path fails or produces an outcome inconsistent with the others, so compatibility is not verified.
- The multiple paths are not identified in the reasoning as an acceptance requirement.

### EXPLAINS_ARTIFACT_BEHAVIOR_FROM_SOURCE

签名：`EXPLAINS_ARTIFACT_BEHAVIOR_FROM_SOURCE(explanation_reasoning: reasoning, source_observation: observation)`

The reasoning explains how an artifact realizes its behavior—including differing behavior across execution contexts—by interpreting specific source constructs present in an observation of the artifact's content.

参数：

- `explanation_reasoning: reasoning`：The reasoning node interpreting source constructs to explain the artifact's behavior.
- `source_observation: observation`：The observation containing the artifact or source content being interpreted.

成立条件：

- The observation contains source or artifact content.
- The reasoning references at least one specific construct, block, directive, or code element in that content.
- The reasoning explains how that construct causes or enables the artifact's behavior, including, where relevant, its differing behavior across execution contexts.

排除条件：

- The reasoning only summarizes test results, restates content, or describes behavior without tying it to specific source constructs.
- The observation does not contain source or artifact content.
- The reasoning references no concrete source construct.

### JUSTIFIES_NUMERICAL_EQUIVALENCE_BY_ERROR_ANALYSIS

签名：`JUSTIFIES_NUMERICAL_EQUIVALENCE_BY_ERROR_ANALYSIS(reasoning: reasoning)`

The reasoning derives or bounds the magnitude of accumulated numerical error expected from a proposed computation and compares that magnitude with the required equivalence tolerance, concluding that the produced results will or will not be accepted as equivalent.

参数：

- `reasoning: reasoning`：The agent text performing the error-magnitude derivation or bound and the comparison against the required tolerance.

成立条件：

- The reasoning quantifies an expected error magnitude or worst-case bound for the proposed computation, for example from the number of accumulation steps and machine epsilon.
- The reasoning explicitly relates that magnitude to the stated tolerance and concludes that the tolerance will or will not be met.

排除条件：

- The reasoning asserts correctness or equivalence without deriving or bounding any error magnitude.
- The quantified quantity concerns something other than numerical accuracy, such as runtime, memory, or cost.
- The error magnitude is only taken from an already reported measurement rather than derived or estimated for the proposed computation.

### PREDICTS_PERFORMANCE_FROM_COMPLEXITY_ESTIMATE

签名：`PREDICTS_PERFORMANCE_FROM_COMPLEXITY_ESTIMATE(reasoning: reasoning)`

The reasoning estimates the time or resource cost of one or more implementations, operations, or commands from operation counts, data sizes, conversion overhead, or algorithmic complexity, and uses that estimate to judge whether a performance requirement will be met or to choose how a command should be executed.

参数：

- `reasoning: reasoning`：The agent text containing the cost, operation-count, or duration estimate and the judgement or execution decision drawn from it.

成立条件：

- The reasoning gives a quantitative cost, operation-count, or duration estimate for at least one implementation, operation, or command, before the corresponding outcome is observed.
- The estimate is used either to conclude that a performance requirement will be met or violated, or to decide how a command should be executed, such as its expected duration, timeout, or background execution.

排除条件：

- The reasoning names a performance requirement without estimating any cost or duration.
- The estimate concerns numerical accuracy or correctness rather than time or resource cost.
- The estimate is stated but no performance judgement or execution decision is drawn from it.

### MIRRORS_REFERENCE_OPERATION_ORDER

签名：`MIRRORS_REFERENCE_OPERATION_ORDER(reasoning: reasoning, observation: observation)`

The reasoning deliberately adopts the evaluation or accumulation order of a reference implementation exposed by an observation, so that the new implementation reproduces the reference's numerical results within the required tolerance.

参数：

- `reasoning: reasoning`：The agent text stating that the new computation follows the reference implementation's order of operations in order to match its results.
- `observation: observation`：The observation containing the reference implementation or its computational procedure, whose operation order can be identified.

成立条件：

- The observation contains an implementation or computational procedure whose sequence of operations can be identified.
- The reasoning explicitly states that the new computation reproduces that same order or sequence of operations.
- The reasoning links the adopted order to matching the reference results within the required tolerance.

排除条件：

- The reasoning only states that results must match, without any reference to reproducing the reference's operation order.
- The referenced content does not describe an implementation or computational procedure.
- The reasoning selects a materially different order for speed or convenience without claiming to reproduce the reference's results through it.

### IMPLEMENTS_DECLARED_PLACEHOLDER_INTERFACE

签名：`IMPLEMENTS_DECLARED_PLACEHOLDER_INTERFACE(implementation_action: action, skeleton_observation: observation)`

A write action supplies the missing bodies of an artifact whose observed skeleton contains explicit unfilled placeholders together with declared interface elements, while preserving those declared names, signatures, and interface contract.

参数：

- `implementation_action: action`：The write action producing the filled-in implementation of the skeleton artifact.
- `skeleton_observation: observation`：The observation showing the artifact with explicit unfilled placeholders and its declared interface elements.

成立条件：

- The observation shows an artifact containing explicit unfilled placeholders or stub bodies together with declared interface elements such as function names, argument order, entry points, or module name.
- The action writes content that supplies those missing bodies while retaining the declared interface elements.

排除条件：

- The action creates a wholly new artifact for which no declared interface was observed.
- The action only reads, inspects, or builds the artifact without supplying the missing bodies.
- The action replaces the declared interface elements with a different interface rather than implementing them.

### VERIFIES_EQUIVALENCE_AGAINST_REFERENCE

签名：`VERIFIES_EQUIVALENCE_AGAINST_REFERENCE(tolerance_reasoning: reasoning, comparison_action: action, deviation_observation: observation)`

The reasoning states a tolerance within which candidate outputs must match an independent reference implementation; the action evaluates candidate and reference computations on identical inputs; and the observation reports quantified deviations or explicit equality that can be judged against that tolerance.

参数：

- `tolerance_reasoning: reasoning`：The agent text stating the required equivalence or tolerance that candidate outputs must meet relative to the reference implementation.
- `comparison_action: action`：The action that runs both the candidate and the reference computation on the same inputs and obtains their differences.
- `deviation_observation: observation`：The observation reporting the quantified differences or explicit equality between candidate and reference outputs.

成立条件：

- The reasoning states a tolerance or equivalence requirement for matching the outputs of an independent reference implementation.
- The action evaluates both the candidate and the reference on identical inputs within the same check.
- The observation reports quantified deviations or explicit equality for the compared quantities, sufficient to judge compliance with the stated tolerance.

排除条件：

- The action runs only the candidate implementation, with no reference computation in the same check.
- The observation reports only an unquantified pass or fail without comparison to reference outputs.
- The comparison uses an absolute expected value rather than an independently computed reference result.
- The reference side merely reuses the candidate's own computation path, so agreement is not informative.

### STAGES_CHEAP_PROBE_BEFORE_COSTLY_VALIDATION

签名：`STAGES_CHEAP_PROBE_BEFORE_COSTLY_VALIDATION(sequencing_reasoning: reasoning, precursor_check_action: action, full_validation_action: action)`

The reasoning orders verification into two tiers, deciding that a fast reduced-scale check is performed first while the expensive full-scale validation is deferred until after that probe, and the corresponding actions execute the reduced check followed by the complete required workload.

参数：

- `sequencing_reasoning: reasoning`：The agent text expressing the intent to run a quick reduced check before the full or expensive validation.
- `precursor_check_action: action`：The action executing the reduced or small-scale check.
- `full_validation_action: action`：The action executing the complete, expensive, required workload after the precursor check.

成立条件：

- The reasoning expresses the intent to perform a quick or small-scale check before the full or expensive validation.
- The precursor action exercises a reduced or small-scale case rather than the complete required workload.
- The full validation action exercises the complete required workload and occurs after the precursor action.

排除条件：

- Only one of the two verification steps is performed.
- The first action already exercises the full workload rather than a reduced case.
- The reasoning does not order the checks by cost or scale.
- The precursor check and the full validation are not linked as stages of the same verification effort.

### BROADENS_VERIFICATION_BEYOND_REQUIRED_CASES

签名：`BROADENS_VERIFICATION_BEYOND_REQUIRED_CASES(reasoning: reasoning)`

The reasoning identifies input conditions or variations that the stated requirements and given test harness do not exercise, and commits to verifying them in order to reduce the risk of undetected failure.

参数：

- `reasoning: reasoning`：The agent text naming extra input variations and stating the intention to test them for additional assurance.

成立条件：

- The reasoning names at least one concrete input variation not exercised by the stated test harness, such as a size edge case, an alternative memory layout, an alternative data type, a malformed input, or an alternative invocation interface.
- The reasoning states that these additional checks will be performed to gain assurance beyond the required tests.

排除条件：

- The reasoning only repeats the tests required by the task specification.
- Additional checks are mentioned without identifying any concrete input variation to be exercised.
- The extra activity substitutes for required verification rather than extending it, with no additional assurance motive stated.

### IDENTIFIES_PERFORMANCE_BOTTLENECK

签名：`IDENTIFIES_PERFORMANCE_BOTTLENECK(reasoning: reasoning)`

The reasoning localizes the dominant share of a measured runtime to a specific stage, component, or operation in the execution pipeline, using timing evidence, and presents that localization as the reason to optimize or redesign that stage.

参数：

- `reasoning: reasoning`：The agent text attributing most of the measured runtime to a specific stage or component and motivating optimization of it.

成立条件：

- The reasoning references a measured runtime, timing breakdown, or comparable quantitative performance evidence.
- The reasoning attributes the dominant cost to an identifiable stage, component, or operation rather than to the system as a whole.
- The reasoning presents the identified bottleneck as the reason to redesign or optimize that stage.

排除条件：

- The reasoning states only that performance is inadequate without locating a dominant cost.
- The reasoning proposes optimizations unrelated to any identified cost contributor.
- The timing evidence is used only to check a threshold, with no stage or component singled out as the dominant cost.

### ANTICIPATES_UNSPECIFIED_EVALUATION_CRITERIA

签名：`ANTICIPATES_UNSPECIFIED_EVALUATION_CRITERIA(reasoning: reasoning)`

The reasoning identifies one or more plausible checks, usage patterns, or evaluation scenarios that an external evaluator, hidden test harness, or checker might apply even though the task specification does not state them, and assesses whether the current solution already satisfies or would survive them.

参数：

- `reasoning: reasoning`：Agent text that names unstated evaluation scenarios an external checker might exercise and assesses the solution's robustness against them.

成立条件：

- The reasoning names at least one specific check, usage pattern, or scenario that is not stated in the provided task requirements.
- The reasoning treats that scenario as a condition an external evaluator or checker might impose on the solution, and assesses whether the solution already handles it or would survive it.

排除条件：

- The reasoning only restates or addresses checks that are explicitly required by the task specification.
- The reasoning merely reports results of checks already executed without hypothesizing an unstated external check.
- The reasoning describes hypothetical environment or user behaviors without connecting them to evaluation or acceptance of the solution.
- The reasoning enumerates a concrete additional input variation and commits to verifying it, rather than assessing robustness against an unstated evaluator check.

### REVISES_HYPOTHESIS_USING_CONTRADICTING_OBSERVATION

签名：`REVISES_HYPOTHESIS_USING_CONTRADICTING_OBSERVATION(prior_reasoning: reasoning, contradicting_observation: observation, revised_reasoning: reasoning)`

A previously stated expectation, hypothesis, or interpretation is replaced or corrected after an observation reports a result incompatible with it, with the revised reasoning explicitly incorporating that contradictory evidence as the reason for the change.

参数：

- `prior_reasoning: reasoning`：The earlier reasoning node stating the expectation, hypothesis, or interpretation that is being revised.
- `contradicting_observation: observation`：The observation reporting a result, error, or measured value that does not match the prior expectation.
- `revised_reasoning: reasoning`：The later reasoning node that corrects or replaces the prior expectation in light of the contradicting observation.

成立条件：

- The prior reasoning asserts a specific expectation, hypothesis, structural assumption, or interpretation that is identifiable.
- The observation reports a result or error that is incompatible with that prior expectation.
- The revised reasoning changes or corrects the prior expectation and refers to the conflicting result as the reason for the change.

排除条件：

- No prior expectation or hypothesis is identifiable in the earlier reasoning.
- The observation adds information without contradicting the prior expectation.
- The revision is unrelated to the observed evidence, or the prior expectation is merely restated unchanged.
- The earlier statement is only a plan of action rather than an expectation or interpretation that could be contradicted.

### DERIVES_DECISION_FROM_MEASURED_RESULT

签名：`DERIVES_DECISION_FROM_MEASURED_RESULT(decision_reasoning: reasoning, measurement_observation: observation)`

The reasoning uses quantitative results reported in an observation to compare candidate options or configurations and select or endorse the one with the more favorable measured outcome, or to establish a measured baseline that a subsequent choice or target must improve upon.

参数：

- `decision_reasoning: reasoning`：The reasoning that compares measured values and makes or endorses a selection, or fixes a numeric baseline for subsequent action.
- `measurement_observation: observation`：The observation reporting the measured values used in the comparison or baseline.

成立条件：

- The observation reports measured quantities, such as metrics, losses, counts, or comparable numeric outcomes, for at least two candidate options or for a quantity used as a baseline.
- The reasoning compares or reuses those quantities to select or endorse a candidate option or to fix a numerical baseline or target for subsequent action.

排除条件：

- The reasoning only repeats the measured numbers without using them to select, endorse, or set a baseline.
- The observation contains no measurement relevant to the decision or baseline.
- The reasoning selects among options using only qualitative considerations with no measured comparison.
- The measurement is used only to check compliance with an already stated external threshold, with no selection among candidates and no baseline derivation.
