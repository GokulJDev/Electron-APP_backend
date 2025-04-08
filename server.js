const express = require('express');
const cors = require('cors');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const mongoose = require('mongoose');
const rateLimit = require('express-rate-limit'); // Import rate limiting
const multer = require('multer');
const dotenv = require('dotenv');
const path = require('path');
const { exec, spawn } = require('child_process');
const fs = require('fs');
dotenv.config();

const User = require('./models/User');
const Project = require('./models/Project');
const Profile = require('./models/Profile');

const storage = multer.diskStorage({
  destination: function (req, file, cb) {
    cb(null, 'KAIRA/Images/uploads/');
  },
  filename: function (req, file, cb) {
    cb(null, Date.now() + '-' + file.originalname);
  }
});

const upload = multer({ storage: storage });

const app = express();
app.use(express.json());
app.use(cors());
app.use('/KAIRA/Images/uploads', express.static(path.join(__dirname, 'KAIRA/Images/uploads')));

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
    
    // console.log('Received Token:', token)
  
    if (!token) {
      return res.status(403).json({ message: 'Access denied. Token is missing.' });
    }
  
    jwt.verify(token, process.env.SECRET_KEY, (err, decoded) => {
      if (err) {
        console.error('JWT Verification Error:', err); // Log error for debugging
        return res.status(401).json({ message: 'Invalid token.' });
      }
  
      req.user = decoded; // Attach decoded user object to request
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
  max: 200,
  message: 'Too many requests, please try again later.'
});
app.use(limiter);

// Register a new user
app.post('/register', async (req, res) => {
  const { username, password, role } = req.body;

  try {
      const existingUser = await User.findOne({ username });
      if (existingUser) {
          return res.status(400).json({ message: 'Username already exists' });
      }

      // Create a new user instance
      const newUser = new User({
          username,
          password,
          role,
      });

      // Save the user to the database
      await newUser.save();

      // Create a profile for the new user
      const newProfile = await Profile.create({
          user: newUser._id,
          username: newUser.username,
      });

      // Link the profile to the user
      newUser.profile = newProfile._id;
      await newUser.save();

      res.status(201).json({ message: 'User registered successfully!' });
  } catch (err) {
      console.error('Error during registration:', err);
      res.status(500).json({ message: 'Error registering user' });
  }
});

// Route to fetch profile details
app.get('/profile', verifyToken, async (req, res) => {
  const userId = req.user.userId;
  try {
    // Find the user by ID and populate the profile
    let user = await User.findById(userId).populate('profile');

    if (!user) {
      return res.status(404).json({ error: 'User not found' });
    }

    // If the user exists but has no profile, create a default profile
    if (!user.profile) {
      const defaultProfile = await Profile.create({
        user: userId,
        username: user.username || 'Default Username',
        gender: 'Prefer not to say', // Default value
        dateOfBirth: new Date('2000-01-01'), // Default value
        country: 'Unknown', // Default value
        address: 'Not provided', // Default value
        preferredLanguage: 'English', // Default value
      });

      user.profile = defaultProfile._id;
      await user.save();

      // Format the dateOfBirth to yyyy-MM-dd
      defaultProfile.dateOfBirth = defaultProfile.dateOfBirth.toISOString().split('T')[0];

      return res.status(200).json({ profile: defaultProfile });
    }

    // Format the dateOfBirth to yyyy-MM-dd
    user.profile.dateOfBirth = user.profile.dateOfBirth.toISOString().split('T')[0];

    // Send the profile details as a response
    res.status(200).json({ profile: user.profile });
  } catch (error) {
    console.error('Error fetching profile details:', error);
    res.status(500).json({ error: 'Internal Server Error' });
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


app.get("/dashboard",verifyToken, async (req, res) => {
  const userId = req.user.userId;

  try {
    const projects = await Project.find({ userId: userId, isDeleted: false }).sort({ updatedAt: -1 });

    const totalProjects = await Project.countDocuments({ userId: userId, isDeleted: false });
    const activeProjects = await Project.countDocuments({ userId: userId, status: 'active', isDeleted: false });

    // Calculate trends
    const oneWeekAgo = new Date();
    oneWeekAgo.setDate(oneWeekAgo.getDate() - 7);

    const projectsThisWeek = await Project.countDocuments({ userId: userId, createdAt: { $gte: oneWeekAgo }, isDeleted: false });
    const projectsThisweekactive = await Project.countDocuments({ userId: userId, createdAt: { $gte: oneWeekAgo }, status: 'active', isDeleted: false });

    const totalTimeSpent = '47h';  // Replace with actual calculation if available
    const totalSize = await Project.aggregate([
      { $match: { userId: userId, isDeleted: false } },
      { $group: { _id: null, totalSize: { $sum: "$fileSize" } } }
    ]);

    const totalSizeInGB = totalSize.length > 0 && totalSize[0].totalSize ? (totalSize[0].totalSize / (1024 * 1024 * 1024)).toFixed(1) : 0;

    const stats = [
      { title: 'Total Projects', value: totalProjects, icon: 'FileText', trend: `+${projectsThisWeek} this week` },
      { title: 'Active Projects', value: activeProjects, icon: 'Activity', trend: `+${projectsThisweekactive} this week` },
      { title: 'Time Spent', value: totalTimeSpent, icon: 'Clock', trend: '12h this week' },
      { title: 'Project Size', value: `${totalSizeInGB}GB`, icon: 'BarChart', trend: '+300MB' },
    ];

    res.json({
      stats,
      projects: projects.map(project => ({
        id: project._id,
        name: project.name,
        lastModified: new Date(project.updatedAt).toLocaleString(),
        size: (project.fileSize / 1024).toFixed(2) + ' KB',
        status: project.status,
      }))
    });
  } catch (err) {
    console.error('Error fetching dashboard data:', err);
    res.status(500).json({ message: 'Internal Server Error' });
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

    // Create the project without the image path
    const newProject = new Project({
      name,
      description,
      tags: tags ? tags.split(",") : [],
      image: image ? `KAIRA/Images/uploads/${image.filename}` : null,
      imageMetadata: image
        ? {
            originalName: image.originalname,
            size: image.size,
            mimeType: image.mimetype,
          }
        : null,
      userId: userId,
      status: "pending",
      fileSize: image ? image.size : 0,
      auditLogs: [
        { action: "Created Project", performedBy: username, details: "Initial project creation" },
      ],
    });

    // Save the project to generate the _id
    await newProject.save();

    console.log("New project ID:", newProject._id);
    res.status(201).json({
      message: "Project created successfully",
      projectId: newProject._id,
      projectName: newProject.name,
      project: newProject,
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
          tags: project.tags.join(', '),
          status: project.status,
          floorPlan: project.image ? `${project.image}` : null,
          projectId: project._id,
      });
  } catch (error) {
      console.error("Error fetching project:", error);
      res.status(500).json({ message: "Internal server error" });
  }
});


app.put('/update/:projectid', upload.fields([{ name: "image" }]), async (req, res) => {
  try {
    const { name, tags, description } = req.body;
    const image = req.files["image"] ? req.files["image"][0] : null;

    // Find the project by ID
    const project = await Project.findById(req.params.projectid);

    if (!project) {
      return res.status(404).json({ message: "Project not found" });
    }

    // If a new image is uploaded, delete the old image file
    if (image && project.image) {
      const oldImagePath = path.join(__dirname, project.image);
      if (fs.existsSync(oldImagePath)) {
        fs.unlinkSync(oldImagePath); // Delete the old image file
      }
    }

    // Update the project with new data
    project.name = name || project.name;
    project.tags = tags ? tags.split(",") : project.tags;
    project.description = description || project.description;
    project.image = image ? `KAIRA/Images/uploads/${image.filename}` : project.image;
    project.status = "active";

    await project.save();

    res.json({
      message: "Project updated successfully",
      project: {
        name: project.name,
        tags: project.tags.join(', '),
        status: project.status,
        description: project.description,
        image: project.image || null,
      },
    });
  } catch (error) {
    console.error("Error updating project:", error);
    res.status(500).json({ message: "Internal server error" });
  }
});


app.post('/blenderProject', async (req, res) => {
  const { image: floorPlan } = req.body;

  if (!floorPlan) {
    return res.status(400).send('Floorplan data is required');
  }

  const scriptPath = path.join(__dirname, './KAIRA/main.py');
  const constPath = path.join(__dirname, './KAIRA/FloorplanToBlenderLib/const.py');
  const iniPath = path.join(__dirname, './Configs/default.ini');
  const targetFolder = path.join(__dirname, './KAIRA/Glb');
  const glbFilePath = path.join(targetFolder, 'floorplan.glb');
  const uploadFolder = path.join(__dirname, './KAIRA/Images/uploads');
  const uploadGlbPath = path.join(uploadFolder, `${Date.now()}-floorplan.glb`);

  // Update the DEFAULT_IMAGE_PATH in const.py
  const constContent = fs.readFileSync(constPath, 'utf8');
  const updatedConstContent = constContent.replace(
    /DEFAULT_IMAGE_PATH = ".*"/,
    `DEFAULT_IMAGE_PATH = "${floorPlan}"`
  );
  fs.writeFileSync(constPath, updatedConstContent, 'utf8');

  // Update the image_path in default.ini
  const iniContent = fs.readFileSync(iniPath, 'utf8');
  const updatedIniContent = iniContent
    .replace(/image_path = ".*"/, `image_path = "${floorPlan}"`)
    .replace(/calibration_image_path = ".*"/, `calibration_image_path = "${floorPlan}"`);
  fs.writeFileSync(iniPath, updatedIniContent, 'utf8');

  const pythonProcess = exec(`start cmd.exe /k python "${scriptPath}" "${floorPlan}"`);

  pythonProcess.stdout.on('data', (data) => {
    console.log(`stdout: ${data}`);
  });

  pythonProcess.stderr.on('data', (data) => {
    console.error(`stderr: ${data}`);
  });

  pythonProcess.on('close', async (code) => {
    console.log(`child process exited with code ${code}`);

    // Check if the .glb file exists
    if (fs.existsSync(glbFilePath)) {
      try {
        // Copy the .glb file to the uploads folder
        fs.copyFileSync(glbFilePath, uploadGlbPath);

        // Update the project with the modelfile path
        const project = await Project.findOne({ name: req.body.projectName }).exec();
        if (!project) {
          return res.status(404).json({ message: 'Project not found' });
        }

        project.modelFile = `KAIRA/Images/uploads/${path.basename(uploadGlbPath)}`;
        await project.save();

        // Send the .glb file to the client
        res.sendFile(glbFilePath, (err) => {
          if (err) {
            console.error('Error sending .glb file:', err);
            res.status(500).send('Error sending .glb file');
          } else {
            console.log('Sent .glb file successfully');
          }
        });
      } catch (err) {
        console.error('Error updating project with modelfile:', err);
        res.status(500).json({ message: 'Error saving modelfile to project' });
      }
    } else {
      res.status(500).send('GLB file not found');
    }
  });
});

app.get("/vrlaunch", async (req, res) => {
  const exePath = path.join(__dirname, "public", "vr", "KAIRA_MAIN.exe");
  console.log("🛠 Trying to launch VR from:", exePath);

  if (!fs.existsSync(exePath)) {
    console.error("❌ File not found at:", exePath);
    return res.status(404).json({ status: "error", message: "VR executable not found" });
  }

  try {
    const process = spawn(exePath, ['-screen-fullscreen', '0', '-screen-width', '1280', '-screen-height', '720'], {
      detached: true,
      stdio: 'ignore'
    });
    

    process.unref();
    console.log("✅ VR launched successfully!");
    res.json({ status: "success", message: "VR launched!" });
  } catch (err) {
    console.error("🔥 Error while launching VR:", err);
    res.status(500).json({ status: "error", message: "Failed to launch VR", error: err.message });
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
