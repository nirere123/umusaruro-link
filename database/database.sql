-- ========================================
-- UMUSARURO LINK DATABASE SCHEMA
-- ========================================
-- This script creates all the necessary tables for the application
-- Run this in MySQL to set up the database

-- Create the database
CREATE DATABASE IF NOT EXISTS umusaruro_link;
USE umusaruro_link;

-- Disable foreign key checks temporarily
SET FOREIGN_KEY_CHECKS = 0;

-- Drop existing tables if they exist (clean setup)
DROP TABLE IF EXISTS trust_history;
DROP TABLE IF EXISTS rentals;
DROP TABLE IF EXISTS equipment;
DROP TABLE IF EXISTS users;

-- Re-enable foreign key checks
SET FOREIGN_KEY_CHECKS = 1;

-- ────────────────────────────────────────
-- USERS TABLE (for all users)
-- ────────────────────────────────────────
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('farmer', 'equip_owner') NOT NULL,
    phone VARCHAR(20),
    location VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ────────────────────────────────────────
-- EQUIPMENT TABLE (equipment listings)
-- ────────────────────────────────────────
CREATE TABLE equipment (
    id INT AUTO_INCREMENT PRIMARY KEY,
    owner_id INT NOT NULL,
    name VARCHAR(150) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    location VARCHAR(100),
    photo VARCHAR(255),
    availability ENUM('available', 'unavailable') DEFAULT 'available',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ────────────────────────────────────────
-- RENTALS TABLE (rental requests)
-- ────────────────────────────────────────
CREATE TABLE rentals (
    id INT AUTO_INCREMENT PRIMARY KEY,
    farmer_id INT NOT NULL,
    equipment_id INT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    status ENUM('pending', 'approved', 'rejected', 'completed', 'cancelled') DEFAULT 'pending',
    total_cost DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (farmer_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (equipment_id) REFERENCES equipment(id) ON DELETE CASCADE
);

-- ────────────────────────────────────────
-- TRUST HISTORY TABLE (for farmers)
-- ────────────────────────────────────────
CREATE TABLE trust_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    farmer_id INT UNIQUE NOT NULL,
    completed_rentals INT DEFAULT 0,
    score DECIMAL(3, 2) DEFAULT 0.00,
    FOREIGN KEY (farmer_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ────────────────────────────────────────
-- CREATE INDEXES for better performance
-- ────────────────────────────────────────
CREATE INDEX idx_equipment_owner ON equipment(owner_id);
CREATE INDEX idx_equipment_availability ON equipment(availability);
CREATE INDEX idx_rentals_farmer ON rentals(farmer_id);
CREATE INDEX idx_rentals_equipment ON rentals(equipment_id);
CREATE INDEX idx_rentals_status ON rentals(status);

