const mongoose = require('mongoose');

const projectSchema = new mongoose.Schema({
    name: {
        type: String,
        required: true,
        minlength: 3,
        maxlength: 50,
    },
    filePath: {
        type: String,  // This will store the file path after upload (with .kaira extension)
        required: true,
        validate: {
            validator: function(v) {
                return v.endsWith('.kaira');  // Ensure the file extension is .kaira
            },
            message: props => `${props.value} must have a .kaira extension!`
        }
    },
    fileMetadata: {
        originalName: String,
        size: Number,
        mimeType: String,
    },
    image: {
        type: String,  // This will store the image path or URL after upload
        validate: {
            validator: function(v) {
                return /^(https?|ftp):\/\/[^\s/$.?#].[^\s]*$/.test(v);
            },
            message: props => `${props.value} is not a valid URL!`
        }
    },
    imageMetadata: {
        originalName: String,
        size: Number,
        mimeType: String,
    },
    description: {
        type: String,
        maxlength: 500,
    },
    status: {
        type: String,
        enum: ['pending', 'in progress', 'completed'],
        default: 'pending',
    },
    tags: [{
        type: String,
        maxlength: 20,
    }],
    userId: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'User',  // Reference to the User model
        required: true,
    },
    createdAt: {
        type: Date,
        default: Date.now,
    },
    updatedAt: {
        type: Date,
        default: Date.now,
    },
    version: {
        type: Number,
        default: 1,
    },
    isDeleted: {
        type: Boolean,
        default: false,
    },
    auditLogs: [{
        action: String,
        performedBy: {
            type: mongoose.Schema.Types.ObjectId,
            ref: 'User',
        },
        performedAt: {
            type: Date,
            default: Date.now,
        },
        details: String,
    }]
},{ collection: 'Projects', timestamps: true });

projectSchema.index({ userId: 1 });
projectSchema.index({ createdAt: -1 });

module.exports = mongoose.model('Project', projectSchema);
