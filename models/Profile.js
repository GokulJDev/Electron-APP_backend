const mongoose = require('mongoose');

// Define the Profile schema
const ProfileSchema = new mongoose.Schema({
    user: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'User',
        required: true,
        unique: true
    },
    firstName: {
        type: String,
        required: true,
        default: 'John'
    },
    lastName: {
        type: String,
        required: true,
        default: 'Doe'
    },
    email: {
        type: String,
        required: true,
        unique: true,
        lowercase: true,
        default: 'john@gmail.com'
    },
    phone: {
        type: String,
        required: true,
        default: '123-456-7890'
    },
    gender: {
        type: String,
        enum: ['Male', 'Female', 'Other', 'Prefer not to say'],
        required: true,
        default:null
    },
    dateOfBirth: {
        type: Date,
        required: true,
        default:null
    },
    username: {
        type: String,
        required: true,
    },
    country: {
        type: String,
        required: true,
        default:null
    },
    address: {
        type: String,
        required: true,
        default:null
    },
    preferredLanguage: {
        type: String,
        required: true,
        default:null
    },
    avatar: {
        type: String,
        default: null
    },
    createdAt: {
        type: Date,
        default: Date.now
    },
    updatedAt: {
        type: Date,
        default: Date.now
    }
}, { timestamps: true });

// Export Profile model
module.exports = mongoose.model('Profile', ProfileSchema);