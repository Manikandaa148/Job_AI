# 📋 Application Tracker Guide

## Overview
The new **Application Tracker** helps you manage your job search process. You can save jobs from the search results and track their progress through different stages on a visual Kanban board.

## 🚀 How to Use

### 1. Save Jobs
1. Go to the **Job Search** page.
2. Find a job you like.
3. Click the **"Track"** button (Bookmark icon) on the job card.
4. The status will change to **"Saved"**.

### 2. Manage Applications
1. Click **"Application Tracker"** in the top navigation bar.
2. You will see your saved jobs on the board.
3. **Drag and Drop** cards to move them between columns:
   - **Saved**: Jobs you are interested in.
   - **Applied**: Jobs you have applied to.
   - **Interviewing**: Jobs where you have an interview scheduled.
   - **Offer**: Jobs where you received an offer! 🎉
   - **Rejected**: Jobs that didn't work out.

### 3. Add Notes (Coming Soon)
- Click on a card to add notes, salary details, and interview dates.

---

## 🤖 New Chatbot Features

The AI Chatbot has been upgraded with new capabilities:

### ✍️ Cover Letter Generator
- Ask: *"Write a cover letter for Software Engineer at Google"*
- The bot will generate a custom cover letter template for you.

### 🎤 Mock Interview
- Ask: *"Interview me about React"* or *"Mock interview for Python"*
- The bot will ask you technical questions to help you prepare.

---

## 🛠 Technical Implementation

- **Database**: New `applications` table to store status and job details.
- **Frontend**: Drag-and-drop interface powered by `@hello-pangea/dnd`.
- **Backend**: REST API endpoints for full CRUD operations on applications.
