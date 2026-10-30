# Digital Library

A digital library platform for discovering, organizing, and reading books online. The project is being developed to bring book discovery, digital reading, personal reading tools, and future AI-powered assistance together in one place.

## Project Goal

The goal of this project is to build a convenient and accessible digital library where readers can browse books, find titles by author or category, access digital book files, and keep track of their reading.

The platform is also planned to support user accounts, Google sign-in, paid access through Stripe, and AI-powered features that can help readers explore and understand books.

## Planned Features

### Book catalog

- Browse books in the library.
- Search for books by title or author.
- Explore books by category.
- View book descriptions, author information, and categories.
- Support PDF and EPUB book files.

### Reader accounts

- Register and sign in with an email address and password.
- Verify an email address.
- Sign in with Google.
- Provide role-based access for users and administrators.

### Personal reading tools

- Add books to a personal reading list.
- Remove books from a reading list.
- Save and update reading progress for each book.

### Digital book access

- Allow administrators to upload and manage book files.
- Let signed-in users access available book files.
- Track basic file information and processing status.

### Payments with Stripe — planned

- Integrate Stripe for secure online payments.
- Support paid plans or purchases, depending on the final product design.
- Control access to paid content or features based on a user's payment status.

### AI-powered features — planned

AI features may be added to help readers interact with the library and its books. Possible features include:

- Book recommendations based on a reader's interests.
- Summaries or explanations of book content.
- Question answering about a book.
- Assistance with discovering books by topic, author, or reading preference.

The exact AI features and the content they can access will be defined as the project develops.

## Current Development Status

This project is under active development. The current codebase includes an initial backend structure and models or endpoints for parts of the following:

- Books, authors, and categories.
- PDF and EPUB book file management.
- User registration and password-based authentication.
- Email verification.
- Google OAuth sign-in flow.
- Reading lists.
- Reading progress.

Stripe payments, AI features, and the complete user-facing reading experience are planned and are not yet implemented.

## Technology Stack

### Backend

- Python
- FastAPI
- SQLAlchemy
- Alembic
- PostgreSQL
- Pydantic

### Authentication and email

- JWT-based access tokens
- Google OAuth
- SMTP email delivery

### Planned integrations

- Stripe for payments
- AI provider integration for future reader-assistance features

## Project Structure

```text
.
├── app/
│   ├── api/          # API routers
│   ├── core/         # Configuration, security, and shared dependencies
│   ├── db/           # Database setup and session management
│   ├── models/       # Database models
│   ├── schemas/      # API request and response schemas
│   └── services/     # Authentication and email services
├── migrations/       # Database migration files
├── tests/            # Automated tests
├── requirements.txt  # Project dependencies
└── README.md