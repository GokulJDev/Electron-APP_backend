const express = require('express');
const cors = require('cors');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const mongoose = require('mongoose');
const rateLimit = require('express-rate-limit'); // Import rate limiting
const dotenv = require('dotenv');
dotenv.config();

const User = require('./models/User');
const Project = require('./models/Project');

const app = express();
app.use(express.json());
app.use(cors());

// MongoDB connection
const connectionString = process.env.MONGO_URI;
mongoose.connect(connectionString)
  .then(() => console.log('Connected to MongoDB Atlas'))
  .catch(err => console.error('Error connecting to MongoDB Atlas:', err));

// Middleware to verify access token
const verifyToken = (req, res, next) => {
  const token = req.headers['authorization']?.split(' ')[1]; // Get token from Authorization header

  if (!token) {
    return res.status(403).json({ message: 'Access denied. No token provided.' });
  }

  jwt.verify(token, process.env.SECRET_KEY, (err, decoded) => {
    if (err) {
      // Handle the error based on token expiration
      if (err.name === 'TokenExpiredError') {
        return res.status(401).json({ message: 'Token expired. Please use the refresh token to get a new access token.' });
      }
      return res.status(401).json({ message: 'Invalid or expired token.' });
    }

    req.user = decoded; // Attach the decoded user to the request object
    next();
  });
};

app.post('/refresh-token', async (req, res) => {
  const refreshToken = req.body.refreshToken;

  if (!refreshToken) {
    return res.status(401).json({ message: 'No refresh token provided.' });
  }

  // Verify the refresh token
  jwt.verify(refreshToken, process.env.REFRESH_SECRET, (err, decoded) => {
    if (err) {
      return res.status(403).json({ message: 'Invalid refresh token.' });
    }

    // Generate a new access token
    const newAccessToken = jwt.sign(
      { userId: decoded.userId, role: decoded.role },
      process.env.SECRET_KEY,
      { expiresIn: '1h' }
    );

    // Send the new access token
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
  const { userId } = req.body;

  try {
    const user = await User.findById(userId);
    if (!user) {
      return res.status(404).json({ message: 'User not found' });
    }

    // Set the user as logged out
    user.isLoggedIn = false;
    await user.save();

    res.json({ message: 'Logout successful' });
  } catch (err) {
    console.error('Logout error:', err);
    res.status(500).json({ message: 'Server error' });
  }
});


// Helper function to handle repeated project checks
const validateProjectFields = (req, res, next) => {
  const { name, filePath, description } = req.body;
  if (!name || !filePath || !description) {
    return res.status(400).json({ message: 'Name, file path, and description are required' });
  }
  next();
};

// Route to create a new project
app.post('/projects', validateProjectFields, async (req, res) => {
  const { name, filePath, description, tags, image, fileMetadata, imageMetadata } = req.body;
  const userId = req.user.userId;

  try {
    const newProject = new Project({
      name,
      filePath,
      description,
      tags,
      userId,
      image,
      fileMetadata,
      imageMetadata,
    });

    await newProject.save();
    res.status(201).json({ message: 'Project created successfully!', project: newProject });
  } catch (err) {
    console.error('Error creating project:', err);
    res.status(500).json({ message: 'Error creating project' });
  }
});

// Route to get all projects of the current user
app.get('/projects', verifyToken, async (req, res) => {
  const userId = req.user.userId;

  try {
    const projects = await Project.find({ userId, isDeleted: false });
    res.json(projects);
  } catch (err) {
    console.error('Error fetching projects:', err);
    res.status(500).json({ message: 'Server error' });
  }
});

// Route to update a project
app.put('/projects/:id', verifyToken, validateProjectFields, async (req, res) => {
  const { id } = req.params;
  const { name, filePath, description, tags, status, image, fileMetadata, imageMetadata } = req.body;

  try {
    const project = await Project.findById(id);
    if (!project) {
      return res.status(404).json({ message: 'Project not found' });
    }

    if (project.userId.toString() !== req.user.userId) {
      return res.status(403).json({ message: 'Access denied' });
    }

    project.name = name || project.name;
    project.filePath = filePath || project.filePath;
    project.description = description || project.description;
    project.tags = tags || project.tags;
    project.status = status || project.status;
    project.image = image || project.image;
    project.fileMetadata = fileMetadata || project.fileMetadata;
    project.imageMetadata = imageMetadata || project.imageMetadata;
    project.updatedAt = new Date();

    await project.save();
    res.json({ message: 'Project updated successfully!', project });
  } catch (err) {
    console.error('Error updating project:', err);
    res.status(500).json({ message: 'Server error' });
  }
});

// Route to delete (soft) a project
app.delete('/projects/:id', verifyToken, async (req, res) => {
  const { id } = req.params;

  try {
    const project = await Project.findById(id);
    if (!project) {
      return res.status(404).json({ message: 'Project not found' });
    }

    if (project.userId.toString() !== req.user.userId) {
      return res.status(403).json({ message: 'Access denied' });
    }

    project.isDeleted = true;
    await project.save();
    res.json({ message: 'Project deleted successfully!', project });
  } catch (err) {
    console.error('Error deleting project:', err);
    res.status(500).json({ message: 'Server error' });
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
