const mongoose = require('mongoose');
const bcrypt = require('bcryptjs');

// Define the User schema with explicit collection name
const UserSchema = new mongoose.Schema({
    username: { type: String, required: true, unique: true },
    password: { type: String, required: true }, // Storing hashed password
    role: { 
        type: String, 
        required: true, 
        enum: ['admin', 'user'], // Valid roles
        default: 'user' // Optional
    },
    lastLogin: { type: Date, default: null },
    isLoggedIn: { type: Boolean, default: false } // Track if user is logged in
}, { collection: 'Users', timestamps: true });

// Pre-save middleware to hash passwords
UserSchema.pre('save', async function (next) {
    if (!this.isModified('password')) return next();
    try {
        this.password = await bcrypt.hash(this.password, 10);
        next();
    } catch (err) {
        next(err);
    }
});

// Add a method to compare passwords
UserSchema.methods.comparePassword = async function (password) {
    try {
        return await bcrypt.compare(password, this.password);
    } catch (err) {
        throw new Error('Error comparing password');
    }
};

// Export User model
module.exports = mongoose.model('User', UserSchema);
