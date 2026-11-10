
Act as a senior full-stack software engineer, Django architect, UI/UX engineer, database designer, security engineer, and payment-integration engineer.
Your task is to design, develop, and deliver a fully functional production-ready web application for DJs and musicians that allows them to monetize live events through paid song requests, event-specific pricing, and audience tips.
The application must be built primarily with:
•	Python 3
•	Django
•	Django REST Framework where appropriate
•	PostgreSQL
•	HTML5
•	CSS3
•	JavaScript
•	Bootstrap or another professional responsive UI framework
•	QR code generation
•	M-Pesa integration for Kenyan payments
•	Django authentication and authorization
•	A clean, modular architecture
Do not only provide a conceptual explanation. Actually implement the application. Generate the complete project structure, source code, database models, views, URLs, templates, forms, JavaScript, CSS, payment integration, QR generation, authentication, migrations, tests, configuration, and setup instructions required to run the application.
________________________________________
1. Application Concept
Build a platform where DJs and musicians (Artists) can create accounts and monetize their live events.
An Artist should be able to:
1.	Create an account.
2.	Log in securely.
3.	Access an Artist dashboard.
4.	Create individual events.
5.	Give each event a name.
6.	Set the event date/time and location.
7.	Set prices in Kenyan Shillings (KES).
8.	Configure the price for song requests.
9.	Configure optional minimum tip amounts.
10.	Generate a unique QR code for each event.
11.	Download/print the QR code.
12.	Place the QR code at their venue.
13.	Receive paid song requests from the audience.
14.	Receive tips from the audience.
15.	View incoming requests in real time or near real time.
16.	Mark requests as accepted, played, rejected, or completed.
17.	View their earnings and transaction history.
The audience does not need to create an account.
The audience should simply:
Scan QR → Event page opens → Choose song/request → Pay → Request is submitted → Artist sees request.
________________________________________
2. User Roles
There should be at least two roles.
A. Artist
Artists are the main users/admins of their own accounts.
An Artist can:
•	Register
•	Log in
•	Log out
•	Reset/change password
•	Edit profile
•	Upload profile image
•	Add stage/artist name
•	Add phone number
•	Create events
•	Edit events
•	Activate/deactivate events
•	Set song request price
•	Set tip options
•	Generate QR codes
•	Download QR codes
•	View song requests
•	View payment status
•	View tips
•	View earnings
•	Manage requests
•	View transaction history
Artists must only be able to access their own events, requests, payments, QR codes, and financial information.
B. Audience
Audience users should not be required to register.
They access an event through a QR code or event URL.
They can:
•	View the artist/event information
•	See the song-request price
•	Enter their name/nickname optionally
•	Enter the requested song
•	Enter artist/song details
•	Add an optional message
•	Choose a tip amount
•	Make payment
•	Receive confirmation
•	See their request status
________________________________________
3. Artist Registration Flow
Implement this exact flow:
Registration
Artist visits:
/register/
They complete:
•	Artist/stage name
•	Full name
•	Email
•	Phone number
•	Password
•	Confirm password
Validate all fields properly.
After successful registration:
DO NOT automatically log the user in.
Instead:
1.	Create the account.
2.	Show a successful registration message.
3.	Redirect the Artist to:
/login/
The login page should clearly indicate that registration was successful.
After login:
Redirect the Artist to the Artist Dashboard.
________________________________________
4. Artist Dashboard
Create a professional dashboard.
The dashboard should display cards such as:
•	Total Events
•	Active Events
•	Total Song Requests
•	Pending Requests
•	Completed Requests
•	Total Earnings
•	Total Tips
•	Pending Payments
Include navigation:
•	Dashboard
•	My Events
•	Create Event
•	Song Requests
•	Payments
•	Earnings
•	Profile
•	Logout
Use a responsive design that works on:
•	Desktop
•	Tablet
•	Mobile
________________________________________
5. Event Creation
Artists must be able to create an event.
Create an event form with fields such as:
•	Event name
•	Event description
•	Venue
•	Location
•	Event date
•	Start time
•	End time
•	Song request price
•	Minimum tip
•	Event status
Example:
Event Name:
Friday Night Live
Venue:
XYZ Lounge
Song Request Price:
KES 200
Minimum Tip:
KES 50
The Artist should be able to set different prices for different events.
For example:
Event A:
Song request = KES 100
Event B:
Song request = KES 300
Event C:
Song request = KES 500
All monetary values must be stored safely as integer/minor units or Decimal values. Never use floating-point values for money.
________________________________________
6. QR Code System
Every event must have a unique QR code.
When an Artist creates an event, automatically generate a QR code containing the public event URL.
Example:
https://yourdomain.com/event/abc123/
The QR code must not expose private Artist information.
Each event should have its own unique public identifier/UUID or secure slug.
The Artist dashboard should provide:
•	View QR Code
•	Download QR Code
•	Print QR Code
•	Copy Event Link
Create a professional QR-code display page suitable for printing.
The printable page should include:
•	Artist/stage name
•	Event name
•	Venue
•	QR code
•	Short instruction such as:
SCAN TO REQUEST A SONG
Pay → Request → Get Your Song Played
Generate the QR code programmatically using a reliable Python QR-code library.
________________________________________
7. Audience Event Page
When someone scans the QR code, they should be taken directly to the specific event.
Example:
/event/<unique-event-id>/
The page should show:
•	Artist name
•	Artist image if available
•	Event name
•	Venue
•	Event date
•	Event description
•	Song request price
•	Tip information
Provide two primary actions:
Request a Song
Send a Tip
The interface should be extremely simple because users will mostly access it from mobile phones.
________________________________________
8. Song Request Flow
The audience selects:
Request a Song
The form should contain:
•	Name/nickname (optional)
•	Song title
•	Artist/singer
•	Optional message/dedication
•	Tip amount (optional)
However, the system must enforce payment before the request becomes visible to the Artist.
The correct flow should be:
1.	Audience enters request.
2.	Server validates the request.
3.	Create a pending request.
4.	Initiate payment.
5.	Audience completes payment.
6.	Payment provider confirms payment through a secure callback/webhook.
7.	Server verifies the transaction.
8.	Only after successful verification:
o	Mark payment as paid.
o	Mark request as paid.
o	Make the request visible to the Artist.
9.	Show audience confirmation.
Never trust the browser/client to tell the server that payment succeeded.
Payment status must be determined by server-side verification/webhooks.
________________________________________
9. Payment System — Kenya
Design the platform specifically for the Kenyan market.
Use Kenyan Shillings (KES).
Implement M-Pesa integration, preferably through the official/appropriate Safaricom Daraja API or a well-structured payment abstraction layer.
The architecture should allow another payment provider to be added later.
Create a payment service layer such as:
payments/services.py
Do not put all payment logic directly inside views.
The payment system should support:
•	Payment initiation
•	STK Push where applicable
•	Transaction/reference generation
•	Callback handling
•	Payment verification
•	Idempotency
•	Failed payments
•	Cancelled payments
•	Pending payments
•	Successful payments
•	Duplicate callback protection
Use environment variables for:
•	M-Pesa consumer key
•	M-Pesa consumer secret
•	Business short code
•	Passkey
•	Callback URL
•	Other credentials
Never hard-code payment credentials in source code.
________________________________________
10. Payment Architecture
Create a reusable transaction model.
For example:
Transaction
Fields may include:
•	UUID
•	Artist
•	Event
•	Request
•	Transaction type
•	Amount
•	Currency
•	Phone number
•	Provider
•	Provider transaction/reference ID
•	Merchant/request ID
•	Status
•	Created timestamp
•	Updated timestamp
•	Raw callback/reference data where appropriate
Transaction types should include:
•	SONG_REQUEST
•	TIP
Statuses should include:
•	PENDING
•	SUCCESS
•	FAILED
•	CANCELLED
Make payment processing idempotent.
If the same callback is received twice, it must not create duplicate payments or duplicate song requests.
________________________________________
11. Tips
Audience members should also be able to send tips.
The event page should have:
Send a Tip
Allow the audience to enter:
•	Name/nickname
•	Tip amount
•	Optional message
•	Phone number
Provide suggested amounts such as:
•	KES 50
•	KES 100
•	KES 200
•	KES 500
•	Custom amount
The tip must also go through payment verification.
After successful payment:
•	Artist sees the tip.
•	Tip appears in earnings.
•	Audience receives confirmation.
________________________________________
12. Artist Request Management
Create a request management screen.
The Artist should see:
| Song | Requested By | Amount | Tip | Status | Time | Action |
Statuses:
•	Pending
•	Accepted
•	Playing
•	Played
•	Rejected
Provide buttons to update the status.
For example:
Accept
Mark Playing
Mark Played
Reject
The Artist should be able to quickly see incoming requests while performing.
Make this interface mobile-friendly.
________________________________________
13. Real-Time / Near Real-Time Requests
Prefer a real-time architecture if practical.
Possible approaches:
•	Django Channels
•	WebSockets
•	Server-Sent Events
•	AJAX polling as a fallback
When a new paid request arrives, the Artist dashboard should update without requiring a full page refresh.
For example:
🎵 New Paid Request
Song: Calm Down
Artist: Rema
Paid: KES 200
Tip: KES 100
Include an optional browser notification/sound for new requests where appropriate.
If Django Channels is used, configure it correctly for development and production.
________________________________________
14. Database Design
Create a proper relational database.
At minimum, consider models such as:
User
Use Django's custom user model if appropriate.
ArtistProfile
Fields:
•	user
•	stage_name
•	bio
•	phone
•	profile_image
•	created_at
•	updated_at
Event
Fields:
•	artist
•	name
•	description
•	venue
•	location
•	date
•	start_time
•	end_time
•	song_request_price
•	minimum_tip
•	unique_public_id
•	qr_code
•	status
•	created_at
•	updated_at
SongRequest
Fields:
•	event
•	artist
•	requester_name
•	song_title
•	song_artist
•	message
•	amount
•	status
•	created_at
•	updated_at
Tip
Fields:
•	event
•	artist
•	requester_name
•	amount
•	message
•	status
•	created_at
•	updated_at
Transaction
Fields required to track payment lifecycle and provider references.
Use appropriate:
•	ForeignKeys
•	UUIDs
•	indexes
•	unique constraints
•	database constraints
Optimize queries where necessary.
________________________________________
15. Security
Treat this as a real financial application.
Implement:
•	CSRF protection
•	Authentication
•	Authorization
•	Secure password hashing
•	Login protection
•	Input validation
•	XSS protection
•	SQL injection protection
•	Secure cookies
•	HTTPS-ready configuration
•	Environment variables
•	Rate limiting where appropriate
•	Payment callback validation
•	Object-level authorization
•	Secure UUID/public event identifiers
•	Protection against duplicate payments
•	Protection against duplicate song requests
•	Server-side price validation
Most importantly:
Never trust price information sent by the audience browser.
The server must obtain the actual song-request price from the Event stored in the database.
Likewise, tip amounts must be validated server-side.
An audience user must not be able to manipulate a request to another event or Artist.
________________________________________
16. Admin Interface
Configure the Django admin interface.
The platform owner/admin should be able to manage:
•	Artists
•	Events
•	Song requests
•	Tips
•	Transactions
•	Payment records
Provide useful filters and search.
For example:
Transaction admin filters:
•	Status
•	Transaction type
•	Artist
•	Event
•	Date
________________________________________
17. Artist Earnings
Create an earnings page.
Display:
•	Total song-request revenue
•	Total tips
•	Gross revenue
•	Successful transactions
•	Pending payments
•	Failed payments
Add date filtering:
•	Today
•	Last 7 days
•	This month
•	Custom date range
Show transaction history.
If possible, include charts for:
•	Daily earnings
•	Song requests
•	Tips
________________________________________
18. Artist Profile
Create an Artist profile page where the Artist can update:
•	Stage name
•	Full name
•	Email
•	Phone
•	Bio
•	Profile image
The public event page should display the stage name and profile image where available.
________________________________________
19. UX/UI Requirements
Create a modern, professional interface.
The application should feel like a real SaaS/payment product, not a basic Django tutorial.
Use:
•	Clean typography
•	Responsive cards
•	Clear buttons
•	Dashboard statistics
•	Toast notifications
•	Modal dialogs where appropriate
•	Loading indicators
•	Payment status indicators
•	Mobile-first audience interface
Use a consistent visual hierarchy.
Artist dashboard:
Desktop-first but responsive.
Audience interface:
Mobile-first.
The QR-code audience experience should require as few clicks as possible.
________________________________________
20. Public Event URL
Use a secure public URL structure such as:
/event/<uuid>/
or:
/e/<secure-slug>/
The URL should identify only the public event.
Do not expose database sequential IDs if avoidable.
________________________________________
21. Request Confirmation
After successful payment, the audience should see a confirmation page.
Example:
Payment Successful
Your song request has been sent to the Artist.
Song:
Calm Down
Artist:
Rema
Amount:
KES 200
Tip:
KES 100
Total:
KES 300
Request ID:
ABC12345
Status:
Paid / Submitted
Do not expose unnecessary sensitive payment information.
________________________________________
22. Payment Failure
If payment fails:
Show:
Payment Failed
Your payment was not completed and your song request has not been submitted.
Provide:
Try Again
Do not show the request to the Artist until payment is confirmed.
________________________________________
23. Event Lifecycle
Events should have statuses such as:
•	Draft
•	Active
•	Completed
•	Cancelled
Only active events should accept requests.
When an event is completed or deactivated:
•	The QR code can still resolve to the event page.
•	The page should indicate that requests are closed.
•	New payments/request submissions must be blocked.
________________________________________
24. Project Structure
Use a clean Django architecture.
For example:
project/
├── manage.py
├── requirements.txt
├── .env.example
├── README.md
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── accounts/
├── artists/
├── events/
├── requests/
├── payments/
├── dashboard/
├── core/
├── templates/
├── static/
├── media/
└── tests/
You may change the structure if you have a better production-grade architecture, but keep responsibilities clearly separated.
________________________________________
25. API
Where useful, expose REST endpoints using Django REST Framework.
Potential endpoints:
POST /api/auth/register/
POST /api/auth/login/

GET /api/events/
POST /api/events/
GET /api/events/<id>/
PUT /api/events/<id>/
DELETE /api/events/<id>/

GET /api/events/<id>/requests/

POST /api/events/<id>/requests/

POST /api/payments/initiate/

POST /api/payments/mpesa/callback/

POST /api/tips/

GET /api/dashboard/stats/
Protect private endpoints with authentication.
Public event endpoints must only expose information intended for the audience.
________________________________________
26. Testing
Do not skip testing.
Create automated tests for:
Authentication
•	Registration
•	Duplicate email
•	Invalid password
•	Login
•	Logout
•	Authorization
Events
•	Event creation
•	Event editing
•	Event ownership
•	Event activation/deactivation
•	Public event access
QR Codes
•	QR generation
•	Correct event URL
•	Unique QR code per event
Song Requests
•	Request creation
•	Price validation
•	Unpaid request not visible to Artist
•	Paid request visible
•	Request status updates
•	Closed event rejects requests
Payments
•	Payment initiation
•	Successful callback
•	Failed callback
•	Duplicate callback
•	Invalid callback
•	Transaction idempotency
Tips
•	Successful tip
•	Failed tip
•	Invalid amount
Security
Test that Artist A cannot access Artist B's:
•	Events
•	Requests
•	Payments
•	Earnings
________________________________________
27. Environment Configuration
Use .env.
Provide:
.env.example
with variables such as:
SECRET_KEY=
DEBUG=False
DATABASE_URL=

MPESA_CONSUMER_KEY=
MPESA_CONSUMER_SECRET=
MPESA_SHORTCODE=
MPESA_PASSKEY=
MPESA_CALLBACK_URL=

ALLOWED_HOSTS=
Never commit secrets.
________________________________________
28. Production Readiness
Configure the project for production.
Include:
•	PostgreSQL
•	Gunicorn
•	ASGI support if using Channels
•	Static files
•	Media files
•	Environment-based configuration
•	Logging
•	Secure headers
•	HTTPS configuration
•	Production settings
•	Database migrations
Provide deployment instructions.
A deployment target such as Render, Railway, DigitalOcean, AWS, or another suitable platform can be used.
Clearly separate development and production configuration.
________________________________________
29. README
Create a comprehensive README.md.
It must explain:
1.	What the application does.
2.	Technologies used.
3.	Project structure.
4.	How to clone/install.
5.	How to create a virtual environment.
6.	How to install dependencies.
7.	How to configure .env.
8.	How to create the database.
9.	How to run migrations.
10.	How to create a superuser.
11.	How to run the development server.
12.	How QR codes work.
13.	How payments work.
14.	How to configure M-Pesa.
15.	How to configure callback URLs.
16.	How to run tests.
17.	How to deploy to production.
________________________________________
30. Development Approach
Do not attempt to build everything as one giant file.
Build the application in logical stages:
Stage 1
Project initialization and configuration.
Stage 2
Custom authentication and Artist registration/login.
Stage 3
Artist dashboard.
Stage 4
Event management.
Stage 5
QR-code generation.
Stage 6
Public audience event pages.
Stage 7
Song-request workflow.
Stage 8
M-Pesa payment integration.
Stage 9
Tips.
Stage 10
Artist request management.
Stage 11
Earnings and analytics.
Stage 12
Real-time updates.
Stage 13
Security hardening.
Stage 14
Automated tests.
Stage 15
Production deployment configuration.
________________________________________
31. Important Payment Rule
This is a critical business requirement:
A song request must NEVER be delivered to the Artist simply because the audience submitted a form.
The lifecycle must be:
Audience scans QR
        ↓
Public event page
        ↓
Audience enters song
        ↓
Server creates pending request
        ↓
Payment initiated
        ↓
M-Pesa payment
        ↓
Payment provider callback
        ↓
Server verifies payment
        ↓
Transaction marked SUCCESS
        ↓
Song request marked PAID
        ↓
Request becomes visible to Artist
        ↓
Artist accepts/plays request
If payment fails:
Payment FAILED
      ↓
Request remains unpaid
      ↓
Artist does NOT see it
Implement this using proper database transactions and idempotency.
________________________________________
32. Important Pricing Rule
The Artist sets the price.
For example:
Event: Saturday Night
Song Request: KES 200
The audience cannot change the KES 200 request price.
Even if someone modifies the HTML or sends a custom API request, the backend must retrieve the price directly from the Event database record.
________________________________________
33. User Experience Example
Artist
John registers:
Stage Name: DJ John
Email: john@example.com
Phone: 0712345678
Password: ********
After registration:
Registration successful.
Please log in.
John logs in.
Dashboard:
Welcome, DJ John

Active Events: 2
Pending Requests: 7
Total Earnings: KES 18,500
Tips: KES 4,200
John creates:
Event:
Friday Night Party

Song Request:
KES 200

Minimum Tip:
KES 50
The system generates a QR code.
John downloads and prints it.
________________________________________
Audience
Someone scans the QR code.
They see:
DJ JOHN

Friday Night Party

Song Request
KES 200

[ Request a Song ]

[ Send a Tip ]
They select:
Song: One Dance
Artist: Drake
They pay KES 200 through M-Pesa.
After successful confirmation:
Payment successful.

Your request has been sent to DJ John.
DJ John's dashboard immediately shows:
NEW REQUEST

One Dance
Drake

Paid: KES 200

[Accept]
[Reject]
________________________________________
34. Code Quality Requirements
Write clean, maintainable code.
Use:
•	PEP 8
•	Type hints where useful
•	Django best practices
•	Class-based views where appropriate
•	Service classes for complex business logic
•	Forms/serializers for validation
•	Reusable templates/components
•	Database constraints
•	Meaningful variable names
•	Proper error handling
•	Logging
•	Automated tests
Avoid:
•	Massive views.py files
•	Duplicated code
•	Hard-coded credentials
•	Hard-coded prices
•	Business logic inside templates
•	Trusting client-side payment status
•	Floating-point monetary calculations
•	Exposing sensitive information
________________________________________
35. Deliverables
At the end of development, provide:
1.	Complete Django source code.
2.	Complete project structure.
3.	All models.
4.	All migrations.
5.	Views.
6.	URLs.
7.	Forms.
8.	Serializers.
9.	Templates.
10.	CSS.
11.	JavaScript.
12.	QR-code generation.
13.	M-Pesa integration.
14.	Payment callback handling.
15.	Authentication.
16.	Artist dashboard.
17.	Audience interface.
18.	Song request system.
19.	Tip system.
20.	Earnings dashboard.
21.	Admin configuration.
22.	Automated tests.
23.	.env.example.
24.	requirements.txt.
25.	README.
26.	Deployment configuration.
________________________________________
36. How You Should Respond While Building
Do not merely tell me what code I should write.
Act as the developer and write the actual implementation.
If the project is too large to output in one response, build it incrementally.
For every stage:
1.	Explain briefly what you are implementing.
2.	Show the exact files being created/modified.
3.	Provide the complete contents of each required file.
4.	Ensure imports and references between files are correct.
5.	Do not leave placeholder implementations such as:
o	TODO
o	implement this later
o	your code here
o	...
o	pseudocode
If a third-party API requires credentials that cannot be provided yet, implement the complete integration architecture, configuration, API client, callback handling, validation, error handling, and sandbox/test configuration, and clearly identify the environment variables that must later be supplied.
Do not claim that a payment integration has been tested against a live M-Pesa account unless it actually has.
________________________________________
37. Final Acceptance Criteria
Consider the application complete only when all of the following work:
•	Artist can register.
•	Artist is redirected to login after registration.
•	Artist can log in.
•	Artist reaches dashboard after login.
•	Artist can create an event.
•	Artist can set event-specific KES pricing.
•	System generates a unique QR code.
•	Artist can download/print the QR code.
•	Audience can scan the QR code.
•	Audience reaches the correct event.
•	Audience can submit a song request.
•	Audience must pay before the request reaches the Artist.
•	Payment is verified server-side.
•	Artist receives the paid request.
•	Artist can update request status.
•	Audience can send tips.
•	Tips are paid and recorded.
•	Artist can view earnings.
•	Transactions are recorded.
•	Duplicate payment callbacks cannot create duplicate transactions.
•	Artists cannot access each other's data.
•	Closed events cannot receive new requests.
•	The application is responsive.
•	Tests pass.
•	The application can be run locally using the README instructions.
Start by creating the Django project architecture and then implement the application systematically. Do not stop at a high-level design.
 
