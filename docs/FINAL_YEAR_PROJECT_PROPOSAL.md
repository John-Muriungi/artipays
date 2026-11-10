# Final-Year Project Proposal

## Artipay: Design and Evaluation of a QR-Based, M-Pesa-Integrated Song Request and Tip Management System for Kenyan Live Music Events

### Proposal cover page

| Item | Details |
|---|---|
| Student name | [Insert full name] |
| Registration number | [Insert registration number] |
| Programme | [Insert degree programme] |
| Department / School | [Insert department and school] |
| Institution | [Insert institution] |
| Supervisor | [Insert supervisor's name] |
| Proposed study period | [Insert academic year / semester] |
| Project system | Artipay |

> **Preparation note:** This proposal is derived from the current Artipay codebase. Replace the bracketed institutional details and adjust the study population, schedule, budget, and formatting to your department's proposal template. The application features described below are present in the repository; user adoption, usability results, production payment performance, and financial impact have not been established by the codebase and are proposed for evaluation rather than presented as findings.

## Abstract

Live music performers often need a practical way to receive song requests and audience tips while continuing to perform. Informal processes can make requests difficult to prioritize, separate from event earnings, and communicate to the artist. This project proposes the evaluation of Artipay, a web-based system designed for Kenyan DJs and musicians. An artist can create an event with a song-request price and minimum tip, publish its public page through a QR code, and manage requests and earnings through an authenticated dashboard. An audience member can submit a request or tip and initiate an M-Pesa payment through Safaricom's Daraja STK Push service.

The existing application is implemented with Django and Python, with PostgreSQL as the intended production database, SQLite as a local fallback, and Django Channels with Redis for production WebSocket messaging and shared caching. Its payment workflow records a transaction, receives a Daraja callback, verifies the checkout status with the provider, checks the expected amount, phone number, and receipt, and only then exposes the paid request to the artist. The proposed study will assess whether this design is functionally correct, usable, secure enough for a controlled academic prototype, and suitable for the intended live-event context.

The study will use an iterative design-and-development process and a mixed-method evaluation. Functional and security-related scenarios will be tested in a controlled environment using mocked provider responses and, subject to access and approval, the Daraja sandbox. A small, purposively selected group of DJs or musicians and event attendees will participate in usability tasks and provide feedback. Quantitative measures will include task completion, time on task, payment-state correctness, and observed errors; qualitative feedback will be coded into usability and operational themes. No real-money payment testing is required for the study. Expected deliverables are the evaluated Artipay prototype, test evidence, findings, documentation, and recommendations for future deployment and research.

**Keywords:** digital payments, M-Pesa, live music, QR code, song requests, tips, Django, usability evaluation, Kenya.

## 1. Introduction

### 1.1 Background

Live performers interact with their audiences while managing a time-sensitive performance. In a busy venue, an audience member may need to approach the artist, write down a request, or use an informal messaging channel. Such approaches can interrupt the performance and can make it harder for the artist to keep track of the request queue, distinguish a paid request from an unpaid one, or review event income later. These concerns are the project's problem framing and will be checked through the proposed requirements discovery; they are not claims of measured prevalence.

Mobile-first web applications and QR codes offer a way to connect a physical event with an online service without requiring attendees to install a dedicated application. For an event-specific page, an audience member can scan a displayed code, review the artist and event, submit a song request or tip, and initiate a mobile payment. For the artist, an event dashboard can collect paid requests and present request status and earnings in one place.

Artipay is an existing Django application developed for this use case in Kenya. The current implementation includes artist registration and profile management, event creation and status control, event-specific KES pricing, public event pages, QR code generation, song requests, tips, Daraja STK Push initiation, callback processing and server-side STK query verification, a request queue, artist earnings views, and authenticated WebSocket notifications with an HTTP polling fallback. This proposal focuses on systematically validating and evaluating that implementation rather than claiming the system has already been deployed or adopted by live performers.

### 1.2 Problem statement

At small or independently organized live music events, the handling of audience song requests and tips may depend on manual interaction and separate payment and note-taking processes. These processes may interrupt the performer, complicate request prioritization, and make it difficult to associate a payment with the correct request or event. The extent and impact of these problems among the intended users have not yet been measured for this project and will be established through preliminary interviews or questionnaires.

Artipay addresses the problem with a QR-accessible, event-specific web workflow that combines request submission, event-defined pricing, M-Pesa payment initiation, provider-side payment verification, and an artist-facing request queue. However, the presence of these features alone does not demonstrate that the end-to-end workflow is reliable, understandable to audience members, useful to artists during an event, or robust against duplicate, delayed, failed, or mismatched payment notifications. A structured evaluation is therefore needed to determine whether the prototype meets its functional requirements and is usable in the intended context, while identifying limitations before any production use.

### 1.3 Aim

To evaluate Artipay as a QR-based, M-Pesa-integrated system for managing paid song requests and tips at Kenyan live music events.

### 1.4 Objectives

1. Document the requirements and usage context of DJs or musicians and event attendees for a digital song-request and tipping workflow.
2. Examine Artipay's event publication, QR access, request and tip submission, payment verification, artist queue, and earnings features against defined functional requirements.
3. Assess usability of the audience checkout journey and artist request-management workflow through structured participant tasks.
4. Evaluate transaction-state correctness and access-control behavior using repeatable tests for successful, failed, cancelled, duplicate, delayed, and mismatched payment scenarios.
5. Identify implementation, operational, and adoption limitations and develop recommendations for improvement and future deployment.

### 1.5 Research questions

1. How effectively does Artipay support the end-to-end workflow from scanning an event QR code to submitting and managing a paid song request or tip?
2. To what extent do intended users complete the audience and artist tasks accurately and with minimal difficulty?
3. Does the payment workflow correctly prevent an unpaid, failed, duplicated, or mismatched payment from being treated as a successful request?
4. What usability, operational, and trust-related improvements do participating DJs, musicians, and attendees recommend?

### 1.6 Rationale and significance

The project is relevant to the practical challenge of coordinating audience participation and mobile payments at live events. The system combines several related functions in one workflow: event-specific pricing, QR-based access, mobile payment initiation, payment verification, and request delivery to the artist. Evaluating these functions together is more informative than testing an isolated payment form or dashboard alone.

Potential beneficiaries include:

- **DJs and musicians:** a consolidated view of paid requests, request progress, event settings, and recorded earnings.
- **Event attendees:** an event-specific mobile web experience for making requests or tips without installing an application.
- **Event organizers:** a potential way to standardize how event-specific requests are submitted and tracked.
- **Researchers and developers:** a documented case study of integrating a third-party mobile payment workflow with a real-time web application.

These are anticipated benefits, not measured outcomes. The proposed study will collect evidence before drawing conclusions about usability or practical value.

## 2. Scope and delimitations

### 2.1 Included in the project

- Artist account registration, authentication, and profile management.
- Artist-owned event creation, editing, activation, completion, and cancellation.
- Event-specific song-request price and minimum tip expressed in whole Kenyan shillings.
- Public event page addressed by a UUID and QR code display, download, and print workflow.
- Anonymous audience submission of song requests and tips.
- M-Pesa Daraja STK Push initiation and transaction status display.
- Callback handling followed by provider-side STK query verification before payment success is recorded.
- Artist request queue with request status progression and real-time notification, plus polling fallback.
- Artist dashboard and transaction/earnings summaries.
- Functional, usability, access-control, and payment-state testing in a controlled environment.

### 2.2 Out of scope

- Processing or storing card details, cash collection, or other payment-provider integrations.
- Artist withdrawals, settlement, escrow, commission calculation, refunds, or dispute resolution.
- Music streaming, song licensing, copyright clearance, or recommendation algorithms.
- Venue discovery, event ticketing, inventory management, or a native Android/iOS application.
- Claiming production readiness, provider certification, commercial performance, or broad market adoption.
- Testing with real customer payments. Any provider interaction will use mocked calls or the Daraja sandbox under approved conditions.

### 2.3 Assumptions and constraints

- Participants can access a smartphone with a browser and, for payment-flow testing, a compatible sandbox or simulated payment journey.
- The study can recruit a small purposive group of intended users within the academic period.
- A Daraja sandbox account and a publicly reachable HTTPS callback endpoint may not be available. If unavailable, provider communication will be mocked and that limitation will be reported.
- Production use requires approved Safaricom credentials, an externally reachable HTTPS callback, shared Redis, durable media storage, and secure hosting configuration. These prerequisites do not imply that the current project has completed production validation.
- The proposed sample and schedule are planning estimates and must be approved by the supervisor and institution.

## 3. Review of the existing system and related concepts

### 3.1 Existing system baseline

Artipay is organized as a Django project with separate applications for accounts, events, music requests, payments, and the dashboard. The source of this proposal's implementation description is the project README, Django models and views, payment service, and existing tests.

| Area | Existing implementation evidence |
|---|---|
| Artist accounts | Registration, login, password reset/change, and artist profile data. |
| Events | Artist-owned events with public UUIDs, status, event date/time, venue/location, request price, and minimum tip. |
| QR and public access | Public event page and generated QR image with print/download views. |
| Requests and tips | Song requests and tips linked to events and artists; prices and tip minimums are validated on the server. |
| Payments | Daraja STK Push initiation, stored transaction identifiers, callback association, STK query verification, and transaction states. |
| Payment integrity | Whole-shilling integer amounts, database constraints, duplicate receipt protection, matching checks for amount and phone, and idempotent callback processing. |
| Artist operations | Request queue, allowed status transitions, earnings summaries, and event totals. |
| Notifications | Authenticated artist WebSocket connection for paid-request notifications; dashboard client also has polling fallback. |
| Infrastructure | Django ASGI, Channels, Redis support, PostgreSQL configuration, SQLite local fallback, and a Render deployment manifest. |
| Tests | Existing account, event, request, callback, payment integrity, and WebSocket tests using Django's test framework and mocked payment calls. |

The repository demonstrates an implemented prototype and automated tests. It does not by itself establish the system's real-world usability, reliability under live network conditions, production Daraja behavior, scalability, user acceptance, or economic benefit. Those are matters for the proposed evaluation.

### 3.2 Related technical concepts

The proposal draws on established software engineering practices: requirements elicitation, iterative implementation, traceable test cases, and evaluation against measurable quality criteria [6]. Web application security concepts are relevant because the system processes account information, phone numbers, event data, and payment references [4]. In particular, authorization must ensure each artist can access only their own private records; payment success must be determined by trusted provider verification rather than user-submitted form data or an unverified callback.

QR codes are used as a physical-to-digital entry point. They reduce the steps needed to reach an event page, but the web page still needs clear event identity, pricing, and payment status so an attendee can make an informed decision. Real-time notifications can reduce the need for repeated page refreshes; a fallback mechanism is important because connectivity and WebSocket support may vary across venues and hosting configurations.

The evaluation will use a software-quality perspective informed by ISO/IEC 25010 [5], with attention to functional suitability, usability, reliability, and security. The study will interpret these dimensions through project-specific acceptance criteria rather than claiming formal certification against the standard.

### 3.3 Research gap

The current prototype brings together QR-based event access, M-Pesa payment initiation, request management, and artist reporting. The identified gap for this project is not that no payment or QR systems exist; rather, this specific integrated workflow has not yet been evaluated with its intended users or through a documented set of payment and access-control edge cases. The proposed study will fill this project-level evidence gap with a controlled evaluation and user feedback.

## 4. Proposed system

### 4.1 System overview

Artipay is a browser-based web application. Artists authenticate to create and manage events. Each event receives a public UUID-based page and a QR code that an artist can display or print. An attendee opens the public page, submits a song request or tip, and supplies a Kenyan mobile number. Artipay obtains the event's price and applicable minimums from server-side records, creates a pending transaction, and requests an M-Pesa STK Push through Daraja [3].

Daraja sends a callback to the configured endpoint. The callback is treated as untrusted input: Artipay associates it with a saved checkout identifier and queries Daraja for the checkout result. On a successful provider response, the application checks the receipt and compares the verified amount and phone number with the saved transaction. Only then is the transaction marked successful and the song request moved from awaiting payment to the artist-visible pending state. A paid request can trigger an artist notification. Failed, cancelled, unverified, or mismatched cases do not expose the request as paid.

### 4.2 Main users and roles

| User | Main activities | Access boundary |
|---|---|---|
| Artist | Register, maintain profile, create and close events, publish a QR code, review requests, advance request status, inspect earnings. | Authenticated access to the artist's own records. |
| Attendee / requester | View an event page, submit a song request or tip, initiate payment, view public payment status/confirmation. | No artist account required; no access to private artist records. |
| Administrator | Use Django administration for authorized platform management. | Restricted administrative account; not a normal attendee workflow. |
| Daraja payment service | Receive STK Push requests, deliver callbacks, and respond to STK query verification. | External provider boundary; credentials and callback configuration kept out of source control. |

### 4.3 Core functional requirements

| ID | Requirement |
|---|---|
| FR-01 | The system shall allow an artist to register, authenticate, and update artist profile information. |
| FR-02 | The system shall allow an authenticated artist to create, edit, activate, complete, or cancel only that artist's events. |
| FR-03 | Each event shall expose a public page and a QR code that resolves to the event page. |
| FR-04 | The system shall accept a new request or tip only while the event is active. |
| FR-05 | The system shall determine request pricing and minimum tip from the saved event settings, not from a client-supplied amount. |
| FR-06 | The system shall validate request/tip data and normalize valid Kenyan mobile numbers before initiating payment. |
| FR-07 | The system shall create a transaction record and initiate a Daraja STK Push for a valid audience submission. |
| FR-08 | The system shall associate a callback with a known checkout identifier and verify the outcome through the Daraja STK query endpoint before crediting a payment. |
| FR-09 | The system shall reject or fail payment processing when the provider result, receipt, amount, or phone details do not satisfy the transaction checks. |
| FR-10 | The system shall handle repeated callbacks without creating duplicate payment effects or exposing a request more than once. |
| FR-11 | The system shall expose a song request to the artist queue only after successful payment verification. |
| FR-12 | The system shall allow the artist to move a paid request through permitted states: pending, accepted, playing, and played; rejection is available from pending. |
| FR-13 | The system shall display payment status to the requester and a confirmation page only for successful payments. |
| FR-14 | The system shall provide an artist dashboard with event, request, transaction, and earnings information scoped to the logged-in artist. |
| FR-15 | The system shall notify a connected authenticated artist when a paid request is available and provide an HTTP polling fallback. |
| FR-16 | The system shall apply rate limits to sensitive login, registration, and public checkout submission endpoints. |

### 4.4 Non-functional requirements and proposed acceptance targets

These targets are proposed for the evaluation. They are not existing measured performance results.

| ID | Quality attribute | Proposed acceptance target |
|---|---|---|
| NFR-01 | Functional correctness | All defined critical acceptance scenarios pass, including active/closed event behavior and request status transitions. |
| NFR-02 | Payment integrity | In the test scenario set, no failed, cancelled, duplicate, unknown, or amount/phone-mismatched payment is recorded as successful or shown as a paid artist request. |
| NFR-03 | Access control | All tested cross-artist access attempts to private events, requests, and earnings are denied. |
| NFR-04 | Usability | At least 80% of participants complete each critical audience and artist task without facilitator intervention; issues are documented even if the target is met. |
| NFR-05 | Efficiency | Record median task completion time for each workflow and compare it with a baseline or participant expectation established during the study. |
| NFR-06 | Responsiveness | On the test setup, target a median response time below 3 seconds for core non-provider pages; report network, hardware, and test conditions. Provider response time is measured separately and excluded from this page-load target. |
| NFR-07 | Resilience | Demonstrate that request visibility and status handling remain correct when notification delivery is unavailable, using the documented polling fallback. |
| NFR-08 | Security practice | Keep credentials in environment configuration, require HTTPS and secure cookies in production settings, validate inputs server-side, and avoid treating the public status UUID as access to private artist data. |
| NFR-09 | Compatibility | Complete key tasks on at least one current desktop browser and one current mobile browser; exact versions are recorded in the test report. |

### 4.5 Data model

The main persisted entities in the current implementation are:

- **ArtistProfile:** one-to-one profile linked to Django's user account, with stage name, phone, biography, and optional profile image.
- **Event:** artist-owned event details, public UUID, date/time, status, song-request price, and minimum tip.
- **SongRequest:** event and artist references, requester/song details, amount, optional tip amount, and request lifecycle status.
- **Tip:** event and artist references, requester details, amount, message, and paid flag.
- **Transaction:** event and artist references, payment type, amount and currency, phone number, provider and checkout identifiers, provider receipt, status, and provider/callback/verification records.

The database uses relationships, uniqueness, indexes, and check constraints for selected integrity conditions. The study will review the suitability of these structures for the specified workflow without proposing unrelated schema changes.

### 4.6 Architecture and technology

| Layer | Current project technology / role |
|---|---|
| Browser interface | Django templates, HTML, CSS, and JavaScript for artist and attendee journeys. |
| Application and business logic | Python with Django; apps are separated by accounts, events, music requests, payments, and dashboard. |
| HTTP and real-time server | Django ASGI application served by Daphne; Django Channels handles artist WebSocket notifications. |
| Persistence | PostgreSQL intended for production; SQLite is configured for local development fallback. |
| Shared runtime services | Redis-compatible cache and Channels layer for production rate limits and multi-process/multi-instance notifications. |
| Payment integration | Safaricom Daraja API for M-Pesa STK Push initiation and server-side STK query verification. |
| QR and image handling | `qrcode` and Pillow. |
| Hosting example | Render service and database configuration in the repository's deployment manifest; other deployment options are described in the deployment checklist. |

**Logical flow** (based on Django's request handling and ASGI/Channels model [1][2]):

```text
Artist browser
    | authenticated HTTP
    v
Artipay / Django ASGI ---- PostgreSQL
    |                            ^
    | public event, checkout     | event, request, transaction records
    v                            |
Attendee browser                 |
    | STK Push request           |
    v                            |
Safaricom Daraja ---- callback -> Artipay payment verification
                                  |
                                  +--> verified paid request --> artist queue
                                  |                              |
                                  +--> Channels/Redis notice --> artist browser
                                  +--> HTTP polling fallback ---> artist browser
```

### 4.7 Security, privacy, and payment controls

The project will be evaluated with a least-privilege and data-minimization mindset:

- Test that artist views and mutations are scoped to the authenticated artist.
- Verify that payment success cannot be set by an attendee's browser submission.
- Verify that the callback is only a trigger for provider verification, not trusted as the sole proof of payment.
- Verify that event price and minimum tip checks are server-side.
- Test repeated, malformed, unknown, delayed, failed, and mismatched callback scenarios.
- Use sandbox credentials only for controlled tests; do not include credentials, full phone numbers, access tokens, or callback personal data in the report.
- Obtain informed consent before collecting participant feedback and use anonymized participant identifiers in study notes.
- Retain only the minimum test data needed and remove or securely dispose of it according to institutional requirements.

The proposal is not a payment-security certification or legal compliance assessment. Production deployment, live money movement, refunds, disputes, and provider approval remain outside the scope.

## 5. Research methodology

### 5.1 Research design

The study will use an applied design-and-evaluation approach. An iterative development process will support requirement confirmation, focused refinement where necessary, and retesting. The evaluation will combine quantitative task and test results with qualitative user feedback. This mixed-method approach is intended to answer both whether the system behaves as specified and how understandable and useful participants find the workflows.

### 5.2 Target population, sampling, and participants

The target population is DJs or musicians who perform at live events in the selected study area, together with adults who attend or have attended such events. A feasible initial plan is purposive recruitment of approximately **5-8 performers and 20-30 attendees**, subject to supervisor approval, ethics requirements, access, and the academic schedule. These numbers are proposed planning estimates, not completed recruitment or statistically representative sample sizes.

Performers will be selected for experience managing live audience requests or tips. Attendees will be selected for familiarity with mobile browsing and, where possible, mobile payments. Participation will be voluntary. Participants under 18 will not be recruited unless the institution's ethics process explicitly approves the required safeguards.

### 5.3 Data collection

1. **Requirements discovery:** brief semi-structured interviews or questionnaires on current request/tip handling, pain points, and workflow expectations.
2. **Functional and security test execution:** execute prepared cases against a controlled test deployment; use mocked Daraja responses and sandbox flows only where safely available.
3. **Usability tasks:** ask participants to scan/open an event page, find event pricing, submit a song request or tip, interpret payment status, and, for performers, review and advance a paid request.
4. **Observation and timing:** record task completion, errors, facilitator interventions, and task duration using participant IDs rather than names.
5. **Post-task feedback:** use a short interview or questionnaire for perceived clarity, trust, ease, and suggested changes. If a standardized usability questionnaire is used, follow its published scoring instructions and cite it in the final report.

### 5.4 Proposed test scenarios

| Test group | Example scenarios | Evidence to record |
|---|---|---|
| Account and access | Register, sign in, reset password; attempt to access another artist's event, queue, or earnings. | Expected/actual result, pass/fail, response code, test notes. |
| Event and QR | Create an event with its own price; open its public page and QR; close the event and attempt a new submission. | Event ownership, QR resolution, page state, whether closed event rejects payment initiation. |
| Pricing and input | Submit a request with a manipulated amount, tip below minimum, invalid phone number, or missing required song information. | Server-calculated amount and whether invalid input is rejected without creating a payable item. |
| Payment success | Simulate successful STK query with matching amount, phone, and unique receipt. | Transaction state, request visibility, confirmation access, artist notification. |
| Payment failure and cancellation | Simulate provider failure and user cancellation. | Transaction state and confirmation that no paid request appears in the artist queue. |
| Integrity and idempotency | Repeat a callback; submit unknown checkout ID; use duplicate receipt; mismatch amount or phone. | No duplicate credit, no false success, correct error/state handling. |
| Notification resilience | Connect an authenticated artist, deliver a paid-request notification, then disable or omit live notification and use polling. | Delivery outcome, authorization, fallback behavior, and observed delay. |
| Usability | Complete the attendee and artist tasks without coaching. | Completion rate, task time, errors, assistance, and participant feedback. |

### 5.5 Data analysis

Quantitative data will be summarized using counts, percentages, medians, and ranges. Measures will include scenario pass rate, task completion rate, median task duration, error count, and facilitator intervention count. Small purposive samples will be treated as descriptive; inferential claims about all Kenyan performers or attendees will not be made.

Qualitative feedback will be organized into themes such as clarity of pricing, confidence in payment status, ease of finding the QR workflow, request queue usefulness, connectivity concerns, and privacy/trust. Where practical, a second reviewer or supervisor will review a subset of coded notes to identify unclear interpretations. Findings will be reported using anonymized participant IDs and short paraphrases; quotations will be used only with consent.

### 5.6 Validity and reliability

- Prepare test cases and expected outcomes before execution.
- Use the same event, account roles, device/browser conditions, and test instructions where comparable.
- Separate provider-network delay from Artipay page and state-processing measurements.
- Repeat critical payment and access-control tests to identify inconsistent behavior.
- Pilot the participant tasks with one or two volunteers and refine confusing instructions before the main sessions.
- Document system version, configuration, browser/device, test date, network conditions, and any mocked or sandboxed provider calls.
- Report recruitment and test-environment limitations so results are interpreted within their proper scope.

### 5.7 Ethical considerations

Participation will be voluntary and based on informed consent. Participants may stop at any point without penalty. No real customer payment will be requested. The preferred test mode is mocked payment responses or a provider sandbox. Any sandbox phone numbers or credentials will be managed as confidential test information and excluded from project materials. Personal data collected in questionnaires or interviews will be minimized, anonymized, stored securely, and retained only for the institutionally approved period. The researcher will obtain any required departmental or institutional ethics approval before recruitment.

## 6. Work plan

The following is a proposed 12-week schedule; it should be aligned with the actual academic calendar.

| Week | Activity | Output |
|---|---|---|
| 1 | Confirm topic, supervisor requirements, and proposal format | Approved project scope |
| 2 | Review related literature and document existing Artipay features | Literature notes and system baseline |
| 3 | Confirm research questions, requirements, and evaluation criteria | Requirements and evaluation plan |
| 4 | Prepare participant materials, consent process, and ethics submission if required | Study instruments and ethics documentation |
| 5 | Review system architecture and prepare test environment | Reproducible test setup |
| 6 | Execute functional, access-control, and payment-state tests | Test results and defects list |
| 7 | Resolve in-scope defects and repeat affected tests | Updated prototype and regression evidence |
| 8 | Pilot usability tasks and refine study instructions | Final participant task script |
| 9 | Recruit participants and conduct performer sessions | Anonymized observations |
| 10 | Conduct attendee sessions and complete data collection | Completed usability dataset |
| 11 | Analyze quantitative and qualitative evidence | Findings and discussion draft |
| 12 | Finalize report, documentation, presentation, and demonstration | Final project package |

## 7. Estimated budget

This is a preliminary estimate in Kenyan shillings (KES), not a supplier quote. The student should replace each figure with current local prices and the institution's budget format.

| Item | Estimated cost (KES) | Basis / note |
|---|---:|---|
| Internet and mobile data | 3,000 | Development, testing, and online research |
| Local transport | 5,000 | Participant recruitment and study sessions |
| Printing and stationery | 1,500 | Consent forms, task sheets, and proposal copies |
| Domain / short-term hosting | 4,000 | Optional public HTTPS test deployment; free/local alternatives may reduce this |
| Participant refreshments / appreciation | 2,000 | Modest, non-coercive provision, subject to ethics approval |
| Contingency | 2,000 | Unplanned study and connectivity costs |
| **Estimated total** | **17,500** | Adjust after local quotation and supervisor review |

The estimate excludes a commercial Safaricom production account, live transaction costs, paid development labor, and production-grade long-term infrastructure. The study should use local development, mocked payment calls, or the sandbox to avoid real payment charges.

## 8. Risks and mitigation

| Risk | Potential effect | Mitigation |
|---|---|---|
| Daraja sandbox credentials or callback access are unavailable | End-to-end provider behavior cannot be tested | Use deterministic mocked responses for application logic; document sandbox testing as a limitation and attempt sandbox verification only if access is granted. |
| Venue connectivity is inconsistent | Live notification or payment flow may be delayed | Test polling fallback and record network conditions; do not claim service-level availability. |
| Participant recruitment is delayed | Reduced evaluation time or sample size | Begin recruitment planning early; use supervisor-approved remote or simulated tasks where appropriate. |
| Participants misunderstand payment state | Incorrect expectations or reduced trust | Use task instructions and observe confusion; treat interface clarity as a study outcome. |
| Test data exposes personal information | Privacy harm | Use synthetic accounts and sandbox data; anonymize notes and restrict access to raw data. |
| Production prerequisites are mistaken for completed work | Misrepresentation of readiness | Clearly label deployment configuration separately from production operation; avoid live payment claims. |
| Scope expands beyond the academic period | Incomplete evaluation | Keep withdrawals, refunds, commissions, native apps, and multi-provider support out of scope. |

## 9. Expected results and deliverables

### 9.1 Expected results

The study is expected to produce evidence on:

- Whether the core event-to-request-to-payment-to-artist workflow behaves according to the defined requirements.
- Whether payment failure, cancellation, duplication, and mismatched details are handled without creating a false paid request.
- Whether intended users can complete the main attendee and artist tasks and where they encounter difficulty.
- Which operational prerequisites and limitations must be addressed before a wider deployment.

The direction and magnitude of usability or performance results are not predetermined. The final report will present observed evidence, including negative or inconclusive results.

### 9.2 Deliverables

1. Final-year project report with background, related work, methodology, implementation baseline, results, discussion, limitations, and recommendations.
2. The Artipay prototype and its source code at the evaluated revision.
3. Requirements and acceptance-test matrix.
4. Functional, payment-integrity, and access-control test evidence.
5. Anonymized usability evaluation summary and analysis.
6. User/admin guidance and deployment notes appropriate to the evaluated environment.
7. Final presentation and controlled demonstration using test or sandbox data.

## 10. Limitations

The proposed sample is small and purposively selected, so findings will not be statistically representative of all artists or event attendees in Kenya. A sandbox cannot fully represent production payment conditions, provider rate limits, financial disputes, intermittent mobile network behavior, or all handset variations. Testing in a controlled environment may not reproduce the interruptions and time pressure of an actual performance. The prototype's current feature set and configuration may also change during the academic period; therefore, the evaluated revision must be recorded. Finally, this project does not establish commercial viability, regulatory compliance, or long-term operational reliability.

## 11. Conclusion

Artipay provides an implemented foundation for connecting event QR access, audience song requests and tips, M-Pesa payment initiation and verification, artist request management, and earnings reporting. A final-year study can contribute meaningful evidence by evaluating the complete workflow rather than relying solely on feature implementation. The proposed research combines repeatable functional and payment-integrity testing with a small usability study involving intended performers and attendees. Its conclusions will be limited to the tested revision, participants, and environment, with sandbox and production boundaries stated transparently.

## References

1. Django Software Foundation. *Django documentation*. https://docs.djangoproject.com/
2. Django Channels. *Channels documentation*. https://channels.readthedocs.io/
3. Safaricom PLC. *Daraja API documentation and developer portal*. https://developer.safaricom.co.ke/
4. OWASP Foundation. *Application Security Verification Standard (ASVS)*. https://owasp.org/www-project-application-security-verification-standard/
5. ISO/IEC. *ISO/IEC 25010:2023 — Systems and software engineering: Product quality model*. International Organization for Standardization, 2023.
6. Pressman, R. S., & Maxim, B. R. *Software Engineering: A Practitioner's Approach*. 9th ed., McGraw-Hill, 2020.

## Appendix A: Suggested participant task checklist

### Attendee tasks

1. Open the public event using a supplied QR code or link.
2. Identify the artist, event status, song-request price, and minimum tip.
3. Submit a song request with valid details and a test phone number.
4. Explain what the displayed payment status means.
5. Complete a separate tip task if included in the session.

### Performer tasks

1. Sign in to the artist account.
2. Create or inspect an event and confirm its request price and minimum tip.
3. Open or download the event QR code.
4. Locate a successfully paid test request in the queue.
5. Advance the request through the permitted lifecycle.
6. Locate the corresponding event or earnings summary.

For each task, record completion (yes/no), time, errors, assistance required, and participant comments. Do not collect real payment credentials or ask participants to make a live payment.

## Appendix B: Suggested critical acceptance checklist

- A closed event cannot initiate a new payment.
- A submitted client amount cannot override the configured event price.
- A tip below the event minimum is rejected.
- An invalid Kenyan mobile number is rejected before payment initiation.
- A callback with an unknown checkout identifier is rejected.
- A callback alone cannot establish payment success without provider-side verification.
- A failed or cancelled provider result leaves the request hidden from the artist queue.
- A successful result with mismatched amount, phone number, or reused receipt is not credited.
- A repeated successful callback does not duplicate transaction effects.
- An artist cannot view or mutate another artist's private event, request, or earnings data.
- An unauthenticated WebSocket connection is rejected.
- If real-time notification is unavailable, the artist can still refresh the request data using the HTTP fallback.
