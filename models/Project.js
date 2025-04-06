const mongoose = require('mongoose');

const projectSchema = new mongoose.Schema({
    name: {
        type: String,
        required: true,
        minlength: 3,
        maxlength: 50,
        unique: true,
    },
    description: {
        type: String,
        maxlength: 500,
    },
    image: {
        type: String, // Stores image file path or URL
        validate: {
            validator: function (v) {
                if (!v) return true; // Allow null or undefined
                return v.startsWith("http://") || 
                       v.startsWith("https://") || 
                       v.startsWith("KAIRA/");
            },
            message: props => `${props.value} is not a valid URL or file path!`
        }        
    },
    imageMetadata: {
        originalName: String,
        size: Number,
        mimeType: String,
    },
    modelFile: {  
        type: String, // Stores 3D model file path or URL
        validate: {
            validator: function (v) {
                return v.startsWith("http://") || 
                       v.startsWith("https://") || 
                       v.startsWith("/uploads/models/");
            },
            message: props => `${props.value} is not a valid 3D model URL or file path!`
        }
    },
    modelMetadata: {  
        originalName: String,
        size: Number,
        format: String, // Example: 'glb', 'fbx', 'obj'
    },
    tags: [{
        type: String,
        maxlength: 20,
    }],
    status: {
        type: String,
        enum: ['pending', 'active', 'completed'],
        default: 'pending',
    },
    userId: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'User',  
        required: true,
    },
    fileSize: {
        type: Number,
        default: 0
    },
    isDeleted: {
        type: Boolean,
        default: false,
    },
    auditLogs: [{
        action: String,
        performedBy: {
            type: String,
            ref: 'User',
        },
        performedAt: {
            type: Date,
            default: Date.now,
        },
        details: String,
    }]
}, { collection: 'Projects', timestamps: true });

projectSchema.index({ userId: 1 });
projectSchema.index({ createdAt: -1 });

module.exports = mongoose.model('Project', projectSchema);
