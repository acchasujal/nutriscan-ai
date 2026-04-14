# NutriScan AI - Product Requirements Document

## Problem

Users find calorie tracking tedious and lack real-time health insights.

## Solution

NutriScan AI enables users to upload a food image and receive:

* Nutritional breakdown
* Health score
* Contextual advice

## Target Users

* Students
* Fitness beginners
* Busy professionals

## Core Features

* AI food recognition (Gemini Vision)
* Nutrition estimation
* Health score (1–10)
* Smart advice
* Meal history (localStorage)

## Success Metrics (AI Grader)

* Code Quality: Clean structure
* Security: Env variables, no key exposure
* Efficiency: Async backend
* Testing: Pytest coverage
* Accessibility: ARIA + semantic HTML
* Google Services: Gemini + Cloud Run

## Constraints

* Repo size < 1MB
* Fast deployment
* No heavy dependencies
