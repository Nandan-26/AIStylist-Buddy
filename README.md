# AIStylist-Buddy 👗✨

> **Your Personal AI Fashion Stylist**

AIStylist-Buddy is an AI-powered personal fashion recommendation application that helps users discover personalized outfits based on their profile, preferences, occasion, style, and fashion requirements.

The application combines **AI-powered outfit recommendations, wardrobe management, AI-generated outfit visualization, and virtual try-on** into one interactive web application.

---

## 🌟 Project Overview

Choosing the right outfit for a particular occasion can be time-consuming, especially when users have many clothing options but are unsure how to combine them.

AIStylist-Buddy addresses this problem by allowing users to create a fashion profile and receive personalized outfit recommendations.

The system considers information such as:

- Personal profile
- Gender
- Age
- Height
- Weight
- Body measurements
- Style preferences
- Color preferences
- Interests
- Occasion
- Season
- Hair preferences
- User's fashion request

The application then provides suitable outfit combinations and allows the user to visualize selected looks using AI.

---

## 🎯 Problem Statement

People often spend significant time deciding:

- What to wear
- Which clothes match together
- What outfit is appropriate for a particular occasion
- Which colors complement each other
- Which hairstyle suits an outfit
- How an outfit might look on them

Traditional fashion recommendation systems may provide generic suggestions without considering the user's personal preferences.

AIStylist-Buddy aims to provide a more personalized fashion experience by combining user information with AI-powered recommendation and image-generation technologies.

---

## 💡 Solution

AIStylist-Buddy provides an integrated fashion assistant where users can:

1. Create an account or sign in with Google.
2. Build their personal fashion profile.
3. Upload a profile photo.
4. Add fashion preferences.
5. Manage their wardrobe.
6. Describe what they want to wear.
7. Select an occasion.
8. Receive personalized outfit recommendations.
9. Generate an AI visualization of a selected outfit.
10. Try an outfit virtually using an AI virtual try-on system.
11. Save favorite looks.
12. View generated images in the AI Gallery.

---

# 🚀 Key Features

## 🔐 1. User Authentication

The application supports two authentication methods:

### Traditional Authentication

Users can:

- Create an account
- Log in
- Log out
- Change their password

Passwords are stored using password hashing rather than storing plain-text passwords.

### Google Authentication

The application also supports Google sign-in using **Streamlit's OpenID Connect authentication**.

The Google authentication flow allows users to:

```text
User
  ↓
Continue with Google
  ↓
Google Authentication
  ↓
Verified Google Identity
  ↓
AIStylist-Buddy Account
  ↓
Personalized Fashion Experience

Google authentication credentials are stored locally in:

.streamlit/secrets.toml

This file is excluded from Git using .gitignore.

👤 2. Personalized Fashion Profile

Users can maintain a personal fashion profile containing information such as:

Name
Age
Gender
Height
Weight
Body measurements
Profile photo
Preferred styles
Preferred colors
Fashion interests
Hair preferences
Taste profile

Profile information is stored in the application's SQLite database.

The profile information is then used as part of the recommendation process.

👕 3. My Wardrobe

Users can manage their wardrobe and clothing items.

The wardrobe system allows the application to work with clothing information when generating outfit recommendations.

The goal is to help users transform individual wardrobe items into complete coordinated looks.

🤖 4. AI Outfit Recommendations

AIStylist-Buddy uses Groq's API for AI-powered text-based outfit recommendations.

The application sends the relevant fashion requirements to the Groq API and requests structured JSON containing outfit information.

The AI can generate details such as:

Outfit name
Top
Bottom
Shoes
Accessories
Colors
Styles
Season
Formality
Trend level
Fabric
Fit

Example:

User Profile
      +
Occasion
      +
Fashion Request
      +
Season
      ↓
Groq AI
      ↓
Structured Outfit Recommendations
      ↓
AIStylist-Buddy UI

The application also contains a built-in outfit catalogue that can be used as a fallback when the online AI recommendation request is unavailable.

🧠 5. Recommendation Logic

The recommendation system combines user requirements with fashion information.

Important inputs include:

User Profile
      +
Occasion
      +
Situation / Request
      +
Style Preferences
      +
Season
      +
Wardrobe Information
      ↓
Recommendation System
      ↓
Recommended Looks

The application prioritizes AI-generated recommendations when the Groq service is available.

If the AI service is unavailable, the application can fall back to the built-in fashion catalogue.

🖼️ 6. AI Outfit Image Generation

AIStylist-Buddy supports AI-generated visualization of a selected outfit.

The current implementation integrates:

FLUX.1 Kontext Dev

through a public Hugging Face ZeroGPU Space using gradio_client.

The user provides a profile photo and selects an outfit.

The application creates a detailed prompt describing:

The selected top
Bottom
Shoes
Accessories
Colors
Fabric
Fit
Hairstyle
Occasion
Additional user styling instructions

The generated image is then saved and displayed inside the application.

Flow:

Selected Outfit
      +
User Profile Photo
      ↓
Prompt Construction
      ↓
FLUX.1 Kontext
      ↓
Generated Fashion Image
      ↓
AI Gallery / Saved Look
Important

AIStylist-Buddy does not train FLUX.1 Kontext from scratch.

It integrates the existing model through a hosted AI service.

👗 7. Virtual Try-On

The application also provides an AI virtual try-on feature.

The current implementation uses:

IDM-VTON

through a Hugging Face/Gradio interface.

The application sends:

User Photo
      +
Garment Image
      +
Garment Description
      ↓
IDM-VTON
      ↓
Virtual Try-On Result

The result is then returned to the application and stored locally.

The current implementation uses:

gradio_client

to communicate with the hosted try-on service.

⚡ 8. Zero-GPU Application Architecture

The main Streamlit application does not require a local NVIDIA GPU for AI image generation or virtual try-on.

Instead, AI processing is delegated to hosted services:

Local Computer
     │
     ├── Streamlit UI
     ├── SQLite Database
     ├── User Profile
     └── Application Logic
              │
              ├──────────────→ Groq API
              │
              ├──────────────→ FLUX.1 Kontext
              │
              └──────────────→ IDM-VTON

Therefore, the local application mainly handles the user interface, database, application logic, and API/service communication.

Note

Hosted AI services can still have:

Queue times
Rate limits
Availability issues
Internet dependency
Processing delays
🎨 9. AI Gallery

Generated fashion images can be stored and displayed through the AI Gallery.

This allows users to revisit previously generated fashion visualizations.

❤️ 10. Saved Looks

Users can save recommended or generated outfits for later use.

Saved looks can be used as a personal collection of preferred fashion combinations.

👤 11. Profile Management

Users can update their profile after registration.

The profile section includes areas for:

Personal details
Photo
Preferences
Hair
Taste profile
Account information

Changes can then be used for future recommendations.

🗄️ Database

AIStylist-Buddy currently uses SQLite for local data storage.

The main database file is:

aistylist.db

The database is used for application data such as:

Users
Profiles
Wardrobe information
Saved looks
Generated images
Feedback
Collections

SQLite was chosen because it is lightweight and suitable for a local/prototype application.

🏗️ System Architecture
                         ┌─────────────────────┐
                         │       USER          │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │   STREAMLIT UI      │
                         │                     │
                         │ Home               │
                         │ Profile            │
                         │ Wardrobe            │
                         │ AI Stylist          │
                         │ Virtual Try-On      │
                         │ AI Gallery          │
                         │ Saved Looks         │
                         └──────────┬──────────┘
                                    │
                     ┌──────────────┼──────────────┐
                     │              │              │
                     ▼              ▼              ▼
              ┌────────────┐ ┌────────────┐ ┌─────────────┐
              │   SQLite   │ │ Groq API   │ │ AI Services │
              │  Database  │ │            │ │             │
              └────────────┘ └────────────┘ │ FLUX        │
                                             │ IDM-VTON    │
                                             └─────────────┘
🔄 Complete User Flow
                    START
                      │
                      ▼
              Login / Register
                      │
          ┌───────────┴───────────┐
          │                       │
          ▼                       ▼
   Username/Password        Google Sign-In
          │                       │
          └───────────┬───────────┘
                      ▼
                 User Profile
                      │
                      ▼
               Profile Photo
                      │
                      ▼
             Fashion Preferences
                      │
                      ▼
                My Wardrobe
                      │
                      ▼
                AI Stylist
                      │
                      ▼
            Select Occasion
                      │
                      ▼
           Enter Fashion Request
                      │
                      ▼
              Groq Recommendation
                      │
                      ▼
             Recommended Looks
                      │
             ┌────────┴─────────┐
             │                  │
             ▼                  ▼
       Generate Image       Virtual Try-On
             │                  │
             ▼                  ▼
          FLUX.1             IDM-VTON
             │                  │
             └────────┬─────────┘
                      ▼
                Generated Image
                      │
              ┌───────┴────────┐
              │                │
              ▼                ▼
          AI Gallery       Saved Looks
🛠️ Technologies Used
Technology	Purpose
Python	Main programming language
Streamlit	Web application and UI
SQLite	Local database
Groq API	AI outfit recommendations
FLUX.1 Kontext Dev	AI outfit image generation
IDM-VTON	Virtual try-on
Gradio Client	Communication with hosted AI Spaces
Google OpenID Connect	Google authentication
Authlib	Authentication support
Requests	HTTP/API communication
Pillow	Image processing
Git	Version control
GitHub	Source code hosting
📦 Main Dependencies

The project uses Python packages for:

Streamlit
Requests
Pillow
Authlib
Gradio Client
Other supporting libraries defined in requirements.txt

Install the project dependencies using:

pip install -r requirements.txt
💻 Installation
1. Clone the Repository
git clone https://github.com/Nandan-26/AIStylist-Buddy.git

Move into the project:

cd AIStylist-Buddy
2. Create a Virtual Environment

Windows:

python -m venv .venv

Activate it:

.\.venv\Scripts\Activate.ps1
3. Install Dependencies
pip install -r requirements.txt
🔑 API Configuration

The application uses secrets that should not be committed to GitHub.

Create:

.streamlit/secrets.toml

Example structure:

GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
GROQ_API_KEY = "YOUR_GROQ_API_KEY"

[auth]
redirect_uri = "http://localhost:8501/oauth2callback"
cookie_secret = "YOUR_RANDOM_SECRET"
client_id = "YOUR_GOOGLE_CLIENT_ID"
client_secret = "YOUR_GOOGLE_CLIENT_SECRET"
server_metadata_url = "https://accounts.google.com/.well-known/openid-configuration"
Important

Never publish real API keys or OAuth client secrets on GitHub.

The following file should remain private:

.streamlit/secrets.toml
🔐 Google OAuth Setup

To enable Google login:

Create a Google Cloud project.
Configure the OAuth consent screen.
Create an OAuth Client ID.
Select:
Application type:
Web application
Add the local redirect URI:
http://localhost:8501/oauth2callback
Add the generated credentials to:
.streamlit/secrets.toml
Start the application.
▶️ Running the Application

From the project directory:

streamlit run app.py

The application will normally open at:

http://localhost:8501
📁 Project Structure
AIStylist-Buddy/
│
├── .git/
│
├── .streamlit/
│   ├── config.toml
│   └── secrets.toml              # Local only - not committed
│
├── .venv/                        # Virtual environment - not committed
│
├── demo_cache/
│
├── sample_wardrobe/
│
├── uploads/
│
├── app.py                        # Main Streamlit application
├── requirements.txt              # Python dependencies
├── aistylist.db                  # Local SQLite database
├── .gitignore
│
└── README.md
🧩 Major Application Modules

The application is organized around several major functional areas.

Home

Landing page and application navigation.

My Wardrobe

User clothing and wardrobe management.

AI Stylist

Personalized fashion recommendation interface.

Virtual Try-On

AI-based garment visualization using IDM-VTON.

AI Gallery

Collection of generated fashion images.

Saved Looks

User's saved outfit recommendations and looks.

Profile

User information, preferences, photo and account settings.

🔌 APIs and External AI Services

AIStylist-Buddy integrates external services rather than implementing every AI model locally.

Groq API

Used for:

Natural-language fashion recommendation

The application sends a structured prompt to Groq and requests JSON-formatted outfit recommendations.

FLUX.1 Kontext

Used for:

AI fashion image generation / outfit visualization

The application sends a user's photo together with an outfit-specific editing prompt.

IDM-VTON

Used for:

Virtual garment try-on

The application sends:

Person Image + Garment Image

and receives a generated try-on result.

Google OpenID Connect

Used for:

Google account authentication

Google handles the authentication process, while AIStylist-Buddy receives the verified user identity.

🧠 Does the Project Use Machine Learning?

Yes, the project integrates AI/ML-based services.

However, the project does not claim to train large generative models from scratch.

The application integrates existing AI models/services for specific tasks:

Groq
  ↓
Text-based fashion recommendations

FLUX.1 Kontext
  ↓
AI image generation / image editing

IDM-VTON
  ↓
Virtual clothing try-on

This is an AI integration project, rather than a project focused on training a large foundation model from scratch.

🖥️ Hardware Requirements

The application is designed to run without requiring a dedicated local GPU for the hosted AI features.

Recommended
CPU: Modern Intel/AMD processor
RAM: 8 GB or more
Storage: 2 GB+ available
Internet: Required for external AI services
OS: Windows / Linux / macOS
Python: Compatible Python 3.x environment

A GPU is not required for the main local Streamlit application.

🌐 Internet Requirement

Internet access is required for features that communicate with external services.

These include:

Google authentication
Groq recommendations
FLUX image generation
IDM-VTON virtual try-on

Local functionality such as SQLite data storage does not inherently require an internet connection.

⚠️ Limitations

The current prototype has several limitations.

1. External AI Dependency

AI features depend on external services.

If an external service is unavailable, rate-limited, or busy, the corresponding feature may fail.

2. Internet Dependency

AI generation and Google authentication require an internet connection.

3. Generation Time

AI image generation and virtual try-on can take longer than normal page interactions.

4. AI Image Accuracy

Generated images may not perfectly preserve:

Clothing details
Body proportions
Facial details
Garment texture
Exact colors

Generative AI output is probabilistic.

5. Virtual Try-On Quality

Virtual try-on quality depends on:

Input photo quality
Garment image quality
Pose
Lighting
AI model availability
Hosted inference resources
6. Prototype Database

SQLite is suitable for a prototype and local application, but a production-scale deployment would typically require a more scalable database architecture.

🔒 Security Considerations

Sensitive credentials should never be committed to GitHub.

The project excludes:

.streamlit/secrets.toml
.env
.venv/
aistylist.db
uploads/*

from version control where appropriate.

API keys should always be stored using environment variables or Streamlit secrets.

🧪 Testing

The application should be tested across the complete user journey:

Registration
     ↓
Login
     ↓
Google Login
     ↓
Profile Creation
     ↓
Photo Upload
     ↓
Preferences
     ↓
Wardrobe
     ↓
AI Recommendation
     ↓
AI Image Generation
     ↓
Virtual Try-On
     ↓
Save Look
     ↓
AI Gallery

Testing should also include failure scenarios such as:

Invalid login
Missing API key
AI service unavailable
Invalid uploaded image
Missing profile photo
Virtual try-on service unavailable
Network timeout
🚧 Future Enhancements

Possible future improvements include:

Real-time camera virtual try-on
Augmented Reality (AR) integration
More advanced body-shape analysis
Better clothing segmentation
Improved outfit-image matching
Larger fashion catalogue
Weather-aware recommendations
Shopping/e-commerce integration
Product recommendations
Size prediction
More hairstyle visualization options
Fashion trend analysis
Mobile application
Cloud database
Production deployment
Improved recommendation evaluation
User feedback-based personalization
AI-generated fashion videos
🎓 Academic / Project Value

AIStylist-Buddy demonstrates practical integration of multiple software and AI concepts:

Python programming
Web application development
Database management
User authentication
OAuth / OpenID Connect
API integration
Natural Language Processing
Generative AI
Computer Vision
Image processing
Recommendation systems
Virtual try-on
Git and GitHub
External AI service integration
👨‍💻 Team
Eswar Nandan Perabattula

Role: Team Leader & Lead Developer

Responsibilities included:

Application architecture
Backend/application logic
Database integration
Recommendation system
AI integration
Authentication
GitHub/repository management
Feature integration
Testing
Lucky

Role: Co-Developer / Frontend & AI Support

Responsibilities:

UI/UX development
Frontend functionality
AI feature support
Virtual try-on interface
Testing
Demo support
Vardan

Role: Co-Developer / Data & Documentation

Responsibilities:

Fashion catalogue/data
Testing
Documentation
Architecture diagrams
Presentation material
Screenshots
Project documentation
📸 Screenshots

Add screenshots of the application here.

Recommended screenshots:

Login
![Login](screenshots/login.png)
Home
![Home](screenshots/home.png)
AI Stylist
![AI Stylist](screenshots/ai-stylist.png)
Recommendations
![Recommendations](screenshots/recommendations.png)
Virtual Try-On
![Virtual Try-On](screenshots/virtual-tryon.png)
AI Gallery
![AI Gallery](screenshots/ai-gallery.png)
Profile
![Profile](screenshots/profile.png)
📚 Project Architecture Summary

The project follows a practical application architecture:

                 ┌─────────────────────┐
                 │       User          │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │    Streamlit UI     │
                 └──────────┬──────────┘
                            │
              ┌─────────────┼─────────────┐
              │             │             │
              ▼             ▼             ▼
         Authentication  Profile      Wardrobe
              │             │             │
              └─────────────┼─────────────┘
                            ▼
                  Recommendation Layer
                            │
                  ┌─────────┴─────────┐
                  │                   │
                  ▼                   ▼
              Groq API          Local Catalogue
                  │                   │
                  └─────────┬─────────┘
                            ▼
                     Recommended Look
                            │
                ┌───────────┴───────────┐
                │                       │
                ▼                       ▼
         FLUX.1 Kontext             IDM-VTON
                │                       │
                ▼                       ▼
        Generated Image          Virtual Try-On
                │                       │
                └───────────┬───────────┘
                            ▼
                    AI Gallery / Saved
📌 What Makes AIStylist-Buddy Different?

AIStylist-Buddy combines multiple fashion-related capabilities in one application.

Instead of only recommending clothing, the system provides a complete flow:

Understand User
       ↓
Understand Occasion
       ↓
Recommend Outfit
       ↓
Visualize Outfit
       ↓
Try Outfit Virtually
       ↓
Save Favorite Look

This creates a more interactive fashion recommendation experience.

🔗 Repository

GitHub:

Nandan-26/AIStylist-Buddy

Repository:

https://github.com/Nandan-26/AIStylist-Buddy

📄 License

This project is currently intended as an academic/prototype project.

Add an appropriate open-source license such as MIT if you decide to distribute the project under an open-source license.

⭐ Acknowledgements

This project makes use of external technologies and services including:

Streamlit
Groq
Hugging Face
FLUX.1 Kontext
IDM-VTON
Gradio
Google OAuth / OpenID Connect

The project integrates these technologies as part of the application rather than claiming ownership of the underlying models.

🙌 Conclusion

AIStylist-Buddy demonstrates how modern AI services can be integrated into a practical fashion application.

By combining:

Personalization + Recommendation + Generative AI + Virtual Try-On + User Authentication + Database Management

the project provides an end-to-end prototype for an AI-assisted personal fashion styling platform.

🚀 Quick Start
git clone https://github.com/Nandan-26/AIStylist-Buddy.git

cd AIStylist-Buddy

python -m venv .venv

.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt

streamlit run app.py

Then open:

http://localhost:8501

AIStylist-Buddy — Your Personal AI Fashion Stylist. 👗✨


### One important correction before you put this on GitHub

The README above says `aistylist.db` is excluded from Git, which matches the **current Git state we checked**. It is therefore better not to say that the database is distributed with the repository.

Also, because your current project uses **Google OAuth + Groq + FLUX + IDM-VTON**, this README is much more accurate for your **current project** than the older README wording that described only the original prototype.

If you want to add this now, the next step is simply to create/update `README.md` with the content above and
