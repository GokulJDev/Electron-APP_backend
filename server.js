const express = require('express');
const cors = require('cors');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const mongoose = require('mongoose');
const rateLimit = require('express-rate-limit'); // Import rate limiting
const multer = require('multer');
const dotenv = require('dotenv');
dotenv.config();

const User = require('./models/User');
const Project = require('./models/Project');

const upload = multer({ dest: 'uploads/' });

const app = express();
app.use(express.json());
app.use(cors());

// MongoDB connection
const connectionString = process.env.MONGO_URI;
mongoose.connect(connectionString)
  .then(() => console.log('Connected to MongoDB Atlas'))
  .catch(err => console.error('Error connecting to MongoDB Atlas:', err));


  const verifyToken = (req, res, next) => {
    const authHeader = req.headers['authorization'];
    
    if (!authHeader) {
      return res.status(403).json({ message: 'Access denied. No token provided.' });
    }
  
    const token = authHeader.split(' ')[1]; // Extract token from "Bearer <token>"
    
    console.log('Received Token:', token); // Log the token to debug
  
    if (!token) {
      return res.status(403).json({ message: 'Access denied. Token is missing.' });
    }
  
    jwt.verify(token, process.env.SECRET_KEY, (err, decoded) => {
      if (err) {
        console.error('JWT Verification Error:', err); // Log error for debugging
        return res.status(401).json({ message: 'Invalid token.' });
      }
  
      req.user = decoded; // Attach decoded user info to request
      next();
    });
  };
  
  
  // Refresh token endpoint
  app.post('/refresh-token', async (req, res) => {
    const { refreshToken } = req.body;
  
    if (!refreshToken) {
      return res.status(401).json({ message: 'No refresh token provided.' });
    }
  
    jwt.verify(refreshToken, process.env.REFRESH_SECRET, (err, decoded) => {
      if (err) {
        console.error('Refresh Token Error:', err); // Logging for debugging
        return res.status(403).json({ message: 'Invalid refresh token.' });
      }
  
      // Generate a new access token
      const newAccessToken = jwt.sign(
        { userId: decoded.userId, role: decoded.role },
        process.env.SECRET_KEY,
        { expiresIn: '1h' }
      );
  
      res.json({ accessToken: newAccessToken });
    });
  });

// Rate limiting to prevent abuse (limit to 100 requests per hour per IP)
const limiter = rateLimit({
  windowMs: 60 * 60 * 1000, // 1 hour
  max: 100,
  message: 'Too many requests, please try again later.'
});
app.use(limiter);

// Register a new user
app.post('/register', async (req, res) => {
  const { username, password, role } = req.body;

  try {
    // Check if the username already exists
    const existingUser = await User.findOne({ username });
    if (existingUser) {
      return res.status(400).json({ message: 'Username already exists' });
    }

    // Create a new user instance
    const newUser = new User({
      username,
      password, // Plaintext password will be hashed by pre-save middleware
      role,
    });

    // Save the user to the database
    await newUser.save();
    res.status(201).json({ message: 'User registered successfully!' });
  } catch (err) {
    console.error('Error during registration:', err);
    res.status(500).json({ message: 'Error registering user' });
  }
});

// Login Route
app.post('/login', async (req, res) => {
  const { username, password } = req.body;

  try {
    // Find the user by username
    const user = await User.findOne({ username });
    if (!user) {
      return res.status(401).json({ message: 'Invalid username or password' });
    }

    // Compare the plaintext password with the hashed password
    const isMatch = await bcrypt.compare(password, user.password);

    if (!isMatch) {
      return res.status(401).json({ message: 'Invalid username or password' });
    }

    // Update lastLogin and isLogin fields
    user.lastLogin = new Date();
    user.isLoggedIn = true;
    await user.save();

    // Generate access token (expires in 1 hour)
    const accessToken = jwt.sign(
      { userId: user._id, role: user.role },
      process.env.SECRET_KEY,
      { expiresIn: '1h' } // Short-lived access token (1 hour)
    );

    // Generate refresh token (expires in 7 days)
    const refreshToken = jwt.sign(
      { userId: user._id, role: user.role },
      process.env.REFRESH_SECRET,
      { expiresIn: '7d' } // Long-lived refresh token (7 days)
    );

    // Send the tokens in the response
    res.status(200).json({
      message: 'Login successful!',
      accessToken, // Access token for future requests
      refreshToken, // Refresh token for getting a new access token
    });
  } catch (err) {
    console.error('Error during login:', err);
    res.status(500).json({ message: 'Error logging in' });
  }
});
// Logout Route
app.post('/logout', async (req, res) => {
  const { token } = req.body; // Get the refresh token from the request body

  try {
    if (!token) {
      return res.status(400).json({ message: 'Token is required' });
    }

    // Verify the token
    const decoded = jwt.verify(token, process.env.REFRESH_SECRET); // Using the refresh token secret
    const userId = decoded.userId; // Assuming the userId is in the token

    // Find the user based on the decoded userId
    const user = await User.findById(userId);
    if (!user) {
      return res.status(404).json({ message: 'User not found' });
    }

    // Set the user as logged out
    user.isLoggedIn = false;
    await user.save();

    res.json({ message: 'Logout successful' });
  } catch (err) {
    if (err.name === 'JsonWebTokenError') {
      return res.status(401).json({ message: 'Invalid token' });
    }
    console.error('Logout error:', err);
    res.status(500).json({ message: 'Server error' });
  }
});

// Endpoint to check if project name exists
app.get("/project/check-name", async (req, res) => {
  const { name } = req.query;

  if (!name) {
    return res.status(400).json({ error: "Project name is required" });
  }

  try {
      // Query the database using the 'name' field
      const existingProject = await Project.exists({ name: name });

      if (existingProject) {
          return res.json({ exists: true });
      }
      return res.json({ exists: false });
  } catch (error) {
      console.error("Error checking project name:", error);
      return res.status(500).json({ error: "Internal server error" });
  }
});


// Route to create a new project
app.post("/project", verifyToken, upload.fields([{ name: "image" }]), async (req, res) => {
  try {
      const { name, description, tags } = req.body;
      const image = req.files["image"] ? req.files["image"][0] : null;
      const userId = req.user.userId;

      // Fetch the username from userId
      const user = await User.findById(userId);
      const username = user ? user.username : "Unknown User";

      const newProject = new Project({
          name,
          description,
          tags: tags ? tags.split(",") : [],
          image: image ? `/uploads/${image.filename}` : null,
          imageMetadata: image ? {
              originalName: image.originalname,
              size: image.size,
              mimeType: image.mimetype,
          } : null,
          userId: userId,
          status: "pending",
          fileSize: image ? image.size : 0, 
          auditLogs: [{ action: "Created Project", performedBy: username, details: "Initial project creation" }]
      });

      await newProject.save();
      console.log("New project ID:", newProject._id);
      res.status(201).json({ 
          message: "Project created successfully", 
          projectId: newProject._id,
          projectName: newProject.name,
          project: newProject 
      });
    

  } catch (error) {
      console.error("Error creating project:", error);
      res.status(500).json({ error: "Internal Server Error" });
  }
});

// Get project details by project name
app.get('/projectdata/:projectName', async (req, res) => {
  try {
      // Find project by name
      const project = await Project.findOne({ name: req.params.projectName }).exec();

      if (!project) {
          return res.status(404).json({ message: "Project not found" });
      }

      res.json({
          name: project.name,
          description: project.description,
          floorPlan: project.image ? `${project.image}` : null,
      });
  } catch (error) {
      console.error("Error fetching project:", error);
      res.status(500).json({ message: "Internal server error" });
  }
});


app.put('/projectdata/:projectName', async (req, res) => {
  try {
    const { name, description, floorPlan } = req.body;

    // Find and update the project
    const updatedProject = await Project.findOneAndUpdate(
      { name: req.params.projectName }, // Find project by name
      { name, description, image: floorPlan }, // Fields to update
      { new: true, runValidators: true } // Return updated document & validate input
    );

    if (!updatedProject) {
      return res.status(404).json({ message: "Project not found" });
    }

    res.json({
      message: "Project updated successfully",
      project: {
        name: updatedProject.name,
        description: updatedProject.description,
        floorPlan: updatedProject.image ? `${updatedProject.image}` : null,
      },
    });
  } catch (error) {
    console.error("Error updating project:", error);
    res.status(500).json({ message: "Internal server error" });
  }
});



app.post("/project/uploadModel", verifyToken, upload.single("modelFile"), async (req, res) => {
  try {
      const { id } = req.params;
      const modelFile = req.file;
      const userId = req.user.userId;

      if (!modelFile) {
          return res.status(400).json({ error: "No 3D model file uploaded" });
      }

      const project = await Project.findById(id);
      if (!project) {
          return res.status(404).json({ error: "Project not found" });
      }

      project.modelFile = `/uploads/models/${modelFile.filename}`;
      project.modelMetadata = {
          originalName: modelFile.originalname,
          size: modelFile.size,
          format: modelFile.mimetype,
      };

      project.auditLogs.push({ action: "Uploaded 3D Model", performedBy: userId, details: "3D model added to project" });

      await project.save();
      res.status(200).json({ message: "3D model uploaded successfully", project });

  } catch (error) {
      console.error("Error uploading 3D model:", error);
      res.status(500).json({ error: "Internal Server Error" });
  }
});



// Start the server
const PORT = process.env.PORT || 3002;
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
app.use((err, _, res, __) => {
  console.error('Unexpected error:', err);
  res.status(500).json({ message: 'Internal server error' });
});
