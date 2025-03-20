# Deployment Guide for ABSecure Backend

This document outlines the step‐by‐step process to deploy the ABSecure FastAPI + MongoDB backend on Render. It covers project preparation, pushing the code to GitHub, configuring the Render web service, setting environment variables (including MongoDB connection details), and verifying that the deployment is successful.

---

## Step 1: Prepare Your Project

1. **Code Structure:**
   - Ensure your project follows a modular structure. For example, your main FastAPI app should be located at `backend/app/main.py`.
   - Verify that all necessary files (e.g., configuration, machine learning code, models, and routes) are organized within the repository.

2. **Requirements File:**
   - Create a `requirements.txt` file listing all required packages. For example:
     ```txt
     fastapi
     uvicorn
     pymongo
     python-dotenv
     pandas
     numpy
     scikit-learn
     joblib
     pydantic
     ```
   - *Tip:* Generate the file using:
     ```bash
     pip freeze > requirements.txt
     ```

3. **Environment Variables:**
   - Your project uses the `MONGO_URI` environment variable to connect to MongoDB.
   - In your local `.env` file, include:
     ```
     MONGO_URI=your_mongo_connection_string
     ```
   - **Production Note:** On Render, you will set these variables via the service settings (see Step 3 below).

---

## Step 2: Push Your Code to GitHub

1. **Repository Setup:**
   - Commit and push all your project files (including the `backend` folder, `requirements.txt`, and any configuration files) to your GitHub repository.
   - Ensure your repository is public or that Render has the necessary permissions to access it.

---

## Step 3: Set Up Your Backend Service on Render

1. **Log in to Render:**
   - Visit the [Render Dashboard](https://dashboard.render.com/) and sign in or create an account.

2. **Create a New Web Service:**
   - Click **“New”** and select **“Web Service”**.
   - Choose **“Connect a Git Repository”** and select your FastAPI project repository from GitHub.
   - Choose the branch you want to deploy (typically `main` or `master`).

3. **Configure the Service:**

   - **Name:** Provide a descriptive name (e.g., `ABSecure-Backend`).
   - **Region:** Choose a region closest to your users.
   - **Build Command:**
     ```bash
     cd backend && pip install -r requirements.txt
     ```
   - **Start Command:**
     Adjust according to your project structure. For example, if your entry point is at `backend/app/main.py`:
     ```bash
     cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000
     ```
   - **Environment Variables:**
     - Add the following key/value pairs:
       - **Key:** `MONGO_URI`  
         **Value:** Your MongoDB connection string from MongoDB Atlas or your managed MongoDB service.
     - **Outbound IP Addresses:**
       - In your MongoDB Atlas (or managed MongoDB) settings, add the outbound IP addresses provided by Render. This step is essential to allow your deployed backend to connect to your MongoDB instance. Refer to the Render documentation for the list of IP addresses to whitelist.

4. **Deployment Options:**
   - You can deploy directly without Docker if your app runs with the above commands.
   - *(Optional)* If you prefer containerized deployment and have a Dockerfile, select the Docker option and adjust the settings accordingly.

5. **Create & Deploy:**
   - Click **“Create Web Service”**. Render will pull your repository, run the build command, and start your service.
   - Monitor the logs in the Render dashboard for any build or runtime errors.

---

## Step 4: Verify the Deployment

1. **Access the Service URL:**
   - Once deployed, Render assigns your service a public URL (e.g., `https://your-backend-app.onrender.com`).

2. **Test Endpoints:**
   - Open a browser and navigate to:
     ```
     https://your-backend-app.onrender.com/docs
     ```
     This will load the FastAPI Swagger UI, where you can view and test all API endpoints (such as your loan and pool routes).

3. **Review Logs & Debug:**
   - Use the Render dashboard to check logs if you encounter any issues, such as errors with environment variables or database connectivity.

---

## Additional Tips

- **Local Testing:**
  - Test your application locally using:
    ```bash
    uvicorn app.main:app --reload
    ```
  - Verify that all endpoints, especially those interacting with MongoDB, work as expected.

- **Database Connectivity:**
  - Ensure your MongoDB instance allows connections from Render by adding Render's outbound IP addresses to your MongoDB whitelist.

- **Security Best Practices:**
  - Avoid hardcoding sensitive information in your code. Always use environment variables for production secrets.

- **scikit-learn Version Alignment:**
  - If you experience issues with scikit-learn version mismatches (e.g., warnings about version differences during model loading), consider updating your dependency to a version with pre-built wheels (like `scikit-learn==1.6.1`) or retrain your model with the version you have pinned.

---

By following these steps, you should have a fully deployed FastAPI + MongoDB backend on Render. If you run into issues, consult Render’s [troubleshooting guide](https://render.com/docs/troubleshooting-deploys) or reach out for further assistance.

