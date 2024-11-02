SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for influencers
-- ----------------------------
DROP TABLE IF EXISTS `influencers`;
CREATE TABLE `influencers`  (
  `influencer_id` int NOT NULL AUTO_INCREMENT,
  `Instagram_Username` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `TikTok_Username` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `Twitter_Username` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `YouTube_ChannelID` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`influencer_id`) USING BTREE,
  UNIQUE INDEX `Instagram_Username`(`Instagram_Username` ASC) USING BTREE,
  UNIQUE INDEX `Tiktok_Username`(`TikTok_Username` ASC) USING BTREE,
  UNIQUE INDEX `Twitter_Username`(`Twitter_Username` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 3 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for instagram_influencer_data_history
-- ----------------------------
DROP TABLE IF EXISTS `instagram_influencer_data_history`;
CREATE TABLE `instagram_influencer_data_history`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `influencer_id` int NULL DEFAULT NULL,
  `followers_count` int NULL DEFAULT NULL,
  `following_count` int NULL DEFAULT NULL,
  `media_count` int NULL DEFAULT NULL,
  `profile_pic_url` varchar(512) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `bio` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `website_url` varchar(512) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `is_verified` tinyint(1) NULL DEFAULT NULL,
  `account_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `last_post_timestamp` datetime NULL DEFAULT NULL,
  `avg_likes` int NULL DEFAULT NULL,
  `avg_comments` int NULL DEFAULT NULL,
  `engagement_rate` decimal(5, 2) NULL DEFAULT NULL,
  `growth_rate` decimal(5, 2) NULL DEFAULT NULL,
  `total_likes` int NULL DEFAULT NULL,
  `total_comments` int NULL DEFAULT NULL,
  `timestamp` datetime NULL DEFAULT CURRENT_TIMESTAMP,
  `bot_flag` tinyint(1) NULL DEFAULT 0,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `influencer_id`(`influencer_id` ASC) USING BTREE,
  CONSTRAINT `influencer_id` FOREIGN KEY (`influencer_id`) REFERENCES `influencers` (`influencer_id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 6 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for instagram_post_data
-- ----------------------------
DROP TABLE IF EXISTS `instagram_post_data`;
CREATE TABLE `instagram_post_data`  (
  `post_id` bigint NOT NULL,
  `influencer_id` int NULL DEFAULT NULL,
  `timestamp` datetime NULL DEFAULT NULL,
  `caption` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `media_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `likes_count` int NULL DEFAULT NULL,
  `comments_count` int NULL DEFAULT NULL,
  PRIMARY KEY (`post_id`) USING BTREE,
  INDEX `instagram_post_data_ibfk_1`(`influencer_id` ASC) USING BTREE,
  CONSTRAINT `instagram_post_data_ibfk_1` FOREIGN KEY (`influencer_id`) REFERENCES `influencers` (`influencer_id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for instagram_post_data_history
-- ----------------------------
DROP TABLE IF EXISTS `instagram_post_data_history`;
CREATE TABLE `instagram_post_data_history`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `post_id` bigint NULL DEFAULT NULL,
  `influencer_id` int NULL DEFAULT NULL,
  `timestamp` datetime NULL DEFAULT CURRENT_TIMESTAMP,
  `likes_count` int NULL DEFAULT NULL,
  `comments_count` int NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `post_id`(`post_id` ASC) USING BTREE,
  INDEX `instagram_post_data_history_ibfk_2`(`influencer_id` ASC) USING BTREE,
  CONSTRAINT `instagram_post_data_history_ibfk_1` FOREIGN KEY (`post_id`) REFERENCES `instagram_post_data` (`post_id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `instagram_post_data_history_ibfk_2` FOREIGN KEY (`influencer_id`) REFERENCES `influencers` (`influencer_id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 41 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for tiktok_profile_history
-- ----------------------------
DROP TABLE IF EXISTS `tiktok_profile_history`;
CREATE TABLE `tiktok_profile_history`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `follower_count` int NULL DEFAULT NULL,
  `video_count` int NULL DEFAULT NULL,
  `avg_likes` int NULL DEFAULT NULL,
  `avg_comments` int NULL DEFAULT NULL,
  `engagement_rate` decimal(5, 2) NULL DEFAULT NULL,
  `growth_rate` decimal(5, 2) NULL DEFAULT NULL,
  `total_likes` int NULL DEFAULT NULL,
  `total_comments` int NULL DEFAULT NULL,
  `bot_flag` tinyint(1) NULL DEFAULT 0,
  `last_updated` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `user_id`(`user_id` ASC) USING BTREE,
  CONSTRAINT `tiktok_profile_history_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `tiktok_profiles` (`user_id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for tiktok_profiles
-- ----------------------------
DROP TABLE IF EXISTS `tiktok_profiles`;
CREATE TABLE `tiktok_profiles`  (
  `user_id` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `nickname` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `follower_count` int NULL DEFAULT NULL,
  `video_count` int NULL DEFAULT NULL,
  `last_updated` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for tiktok_video_history
-- ----------------------------
DROP TABLE IF EXISTS `tiktok_video_history`;
CREATE TABLE `tiktok_video_history`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `video_id` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `view_count` int NULL DEFAULT NULL,
  `like_count` int NULL DEFAULT NULL,
  `comment_count` int NULL DEFAULT NULL,
  `timestamp` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `video_id`(`video_id` ASC) USING BTREE,
  CONSTRAINT `tiktok_video_history_ibfk_1` FOREIGN KEY (`video_id`) REFERENCES `tiktok_videos` (`video_id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for tiktok_videos
-- ----------------------------
DROP TABLE IF EXISTS `tiktok_videos`;
CREATE TABLE `tiktok_videos`  (
  `video_id` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `user_id` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `create_time` datetime NULL DEFAULT NULL,
  `view_count` int NULL DEFAULT NULL,
  `like_count` int NULL DEFAULT NULL,
  `comment_count` int NULL DEFAULT NULL,
  `last_updated` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`video_id`) USING BTREE,
  INDEX `user_id`(`user_id` ASC) USING BTREE,
  CONSTRAINT `tiktok_videos_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `tiktok_profiles` (`user_id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for youtube_channel_history
-- ----------------------------
DROP TABLE IF EXISTS `youtube_channel_history`;
CREATE TABLE `youtube_channel_history`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `channel_id` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `subscriber_count` int NULL DEFAULT NULL,
  `view_count` bigint NULL DEFAULT NULL,
  `video_count` int NULL DEFAULT NULL,
  `avg_likes` int NULL DEFAULT NULL,
  `avg_comments` int NULL DEFAULT NULL,
  `engagement_rate` decimal(5, 2) NULL DEFAULT NULL,
  `growth_rate` decimal(5, 2) NULL DEFAULT NULL,
  `total_likes` int NULL DEFAULT NULL,
  `total_comments` int NULL DEFAULT NULL,
  `bot_flag` tinyint(1) NULL DEFAULT 0,
  `last_updated` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `channel_id`(`channel_id` ASC) USING BTREE,
  CONSTRAINT `youtube_channel_history_ibfk_1` FOREIGN KEY (`channel_id`) REFERENCES `youtube_channels` (`channel_id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 13 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for youtube_channels
-- ----------------------------
DROP TABLE IF EXISTS `youtube_channels`;
CREATE TABLE `youtube_channels`  (
  `channel_id` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `channel_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `subscriber_count` int NULL DEFAULT NULL,
  `view_count` bigint NULL DEFAULT NULL,
  `video_count` int NULL DEFAULT NULL,
  `last_updated` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`channel_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for youtube_video_history
-- ----------------------------
DROP TABLE IF EXISTS `youtube_video_history`;
CREATE TABLE `youtube_video_history`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `video_id` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `view_count` int NULL DEFAULT NULL,
  `like_count` int NULL DEFAULT NULL,
  `comment_count` int NULL DEFAULT NULL,
  `last_updated` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `video_id`(`video_id` ASC) USING BTREE,
  CONSTRAINT `youtube_video_history_ibfk_1` FOREIGN KEY (`video_id`) REFERENCES `youtube_videos` (`video_id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 6 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for youtube_videos
-- ----------------------------
DROP TABLE IF EXISTS `youtube_videos`;
CREATE TABLE `youtube_videos`  (
  `video_id` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `channel_id` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `title` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `view_count` int NULL DEFAULT NULL,
  `like_count` int NULL DEFAULT NULL,
  `comment_count` int NULL DEFAULT NULL,
  `published_at` datetime NULL DEFAULT NULL,
  `last_updated` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`video_id`) USING BTREE,
  INDEX `channel_id`(`channel_id` ASC) USING BTREE,
  CONSTRAINT `youtube_videos_ibfk_1` FOREIGN KEY (`channel_id`) REFERENCES `youtube_channels` (`channel_id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

SET FOREIGN_KEY_CHECKS = 1;
