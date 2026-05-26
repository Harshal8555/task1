-- Create the database if it doesn't exist
CREATE DATABASE IF NOT EXISTS `product_system`;
USE `product_system`;

-- 1. Create 'users' table
CREATE TABLE IF NOT EXISTS `users` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `email` VARCHAR(191) UNIQUE NOT NULL,
    `password` VARCHAR(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. Create 'products' table
CREATE TABLE IF NOT EXISTS `products` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(191) NOT NULL,
    `price` DECIMAL(10, 2) NOT NULL,
    `description` TEXT NOT NULL,
    `image` VARCHAR(500) NOT NULL,
    `category` VARCHAR(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. Seed default admin user (email: admin@example.com, password: admin123)
-- Using Flask Werkzeug security scrypt hash
INSERT INTO `users` (`id`, `email`, `password`)
VALUES (1, 'admin@example.com', 'scrypt:32768:8:1$GBKGrRuqgwjaUYeh$6a5dd9b1f0663ccbeb00fc1f027f955fe88bdfbb0b23990b931e067c5e3fee7d363dfc84973463ffe3338ddba21b27a475581bcab376b8d50bb92cf899ee7609')
ON DUPLICATE KEY UPDATE `password` = VALUES(`password`);

-- 4. Seed initial products for demonstration
INSERT INTO `products` (`id`, `name`, `price`, `description`, `image`, `category`)
VALUES
(1, 'Quantum Pro Wireless Headphones', 129.99, 'Experience premium noise-canceling audio with 40-hour battery life, high-fidelity sound, and memory foam cushions.', 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=600&q=80', 'Electronics'),
(2, 'VeloFit Smart Fitness Watch', 79.50, 'Track your heart rate, sleep cycle, daily steps, and workout routes with this sleek, waterproof smartwatch featuring a AMOLED touch display.', 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=600&q=80', 'Electronics'),
(3, 'AeroStride Running Shoes', 95.00, 'Engineered with breathable mesh fabric, impact-absorbing midsoles, and slip-resistant rubber soles for ultimate comfort during marathons.', 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=600&q=80', 'Fashion'),
(4, 'ErgoFlex Premium Office Chair', 249.00, 'Features high-back lumbar support, adjustable 3D armrests, breathable mesh, and smooth-rolling caster wheels for optimal office comfort.', 'https://images.unsplash.com/photo-1505797149-43b0069ec26b?auto=format&fit=crop&w=600&q=80', 'Furniture'),
(5, 'Barista Express Espresso Maker', 189.99, 'Brew barista-quality espresso, cappuccinos, and lattes at home with a 15-bar Italian pump, milk frother, and automated grinding system.', 'https://images.unsplash.com/photo-1517256064527-09c53b2d0bc6?auto=format&fit=crop&w=600&q=80', 'Kitchen')
ON DUPLICATE KEY UPDATE
  `name` = VALUES(`name`),
  `price` = VALUES(`price`),
  `description` = VALUES(`description`),
  `image` = VALUES(`image`),
  `category` = VALUES(`category`);
