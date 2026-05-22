// Google Analytics Tracking Module
import { analytics } from './firebase-config.js';
import { logEvent } from "https://www.gstatic.com/firebasejs/10.8.0/firebase-analytics.js";

// Track page views
export function trackPageView(pageName) {
    try {
        logEvent(analytics, 'page_view', {
            page_title: pageName,
            page_location: window.location.href,
            page_path: window.location.pathname
        });
        console.log(`📊 Analytics: Page view tracked - ${pageName}`);
    } catch (error) {
        console.error('Analytics error:', error);
    }
}

// Track user sign-in
export function trackSignIn(method = 'google') {
    try {
        logEvent(analytics, 'login', {
            method: method
        });
        console.log(`📊 Analytics: Sign-in tracked - ${method}`);
    } catch (error) {
        console.error('Analytics error:', error);
    }
}

// Track user sign-up
export function trackSignUp(method = 'google') {
    try {
        logEvent(analytics, 'sign_up', {
            method: method
        });
        console.log(`📊 Analytics: Sign-up tracked - ${method}`);
    } catch (error) {
        console.error('Analytics error:', error);
    }
}

// Track profile creation
export function trackProfileCreation(domain, experienceLevel) {
    try {
        logEvent(analytics, 'profile_created', {
            domain: domain,
            experience_level: experienceLevel
        });
        console.log(`📊 Analytics: Profile created - ${domain}, ${experienceLevel}`);
    } catch (error) {
        console.error('Analytics error:', error);
    }
}

// Track assessment completion
export function trackAssessmentComplete(skillCount, averageLevel) {
    try {
        logEvent(analytics, 'assessment_complete', {
            skill_count: skillCount,
            average_level: averageLevel
        });
        console.log(`📊 Analytics: Assessment completed - ${skillCount} skills`);
    } catch (error) {
        console.error('Analytics error:', error);
    }
}

// Track learning path generation
export function trackLearningPathGenerated(courseCount, aiGenerated = true) {
    try {
        logEvent(analytics, 'learning_path_generated', {
            course_count: courseCount,
            ai_generated: aiGenerated
        });
        console.log(`📊 Analytics: Learning path generated - ${courseCount} courses`);
    } catch (error) {
        console.error('Analytics error:', error);
    }
}

// Track course start
export function trackCourseStart(courseTitle, provider) {
    try {
        logEvent(analytics, 'course_start', {
            course_title: courseTitle,
            provider: provider
        });
        console.log(`📊 Analytics: Course started - ${courseTitle}`);
    } catch (error) {
        console.error('Analytics error:', error);
    }
}

// Track course completion
export function trackCourseComplete(courseTitle, provider) {
    try {
        logEvent(analytics, 'course_complete', {
            course_title: courseTitle,
            provider: provider
        });
        console.log(`📊 Analytics: Course completed - ${courseTitle}`);
    } catch (error) {
        console.error('Analytics error:', error);
    }
}

// Track daily tasks generation
export function trackDailyTasksGenerated(totalTasks) {
    try {
        logEvent(analytics, 'daily_tasks_generated', {
            total_tasks: totalTasks
        });
        console.log(`📊 Analytics: Daily tasks generated - ${totalTasks} tasks`);
    } catch (error) {
        console.error('Analytics error:', error);
    }
}

// Track task completion
export function trackTaskComplete(taskTitle, day) {
    try {
        logEvent(analytics, 'task_complete', {
            task_title: taskTitle,
            day: day
        });
        console.log(`📊 Analytics: Task completed - ${taskTitle}`);
    } catch (error) {
        console.error('Analytics error:', error);
    }
}

// Track AI chatbot usage
export function trackChatbotMessage(messageType = 'user_question') {
    try {
        logEvent(analytics, 'chatbot_interaction', {
            message_type: messageType
        });
        console.log(`📊 Analytics: Chatbot interaction - ${messageType}`);
    } catch (error) {
        console.error('Analytics error:', error);
    }
}

// Track quiz generation
export function trackQuizGenerated(topic, level) {
    try {
        logEvent(analytics, 'quiz_generated', {
            topic: topic,
            level: level
        });
        console.log(`📊 Analytics: Quiz generated - ${topic}`);
    } catch (error) {
        console.error('Analytics error:', error);
    }
}

// Track quiz completion
export function trackQuizComplete(topic, score, totalQuestions) {
    try {
        logEvent(analytics, 'quiz_complete', {
            topic: topic,
            score: score,
            total_questions: totalQuestions,
            percentage: Math.round((score / totalQuestions) * 100)
        });
        console.log(`📊 Analytics: Quiz completed - ${score}/${totalQuestions}`);
    } catch (error) {
        console.error('Analytics error:', error);
    }
}

// Track notes generation
export function trackNotesGenerated(topic, level) {
    try {
        logEvent(analytics, 'notes_generated', {
            topic: topic,
            level: level
        });
        console.log(`📊 Analytics: Notes generated - ${topic}`);
    } catch (error) {
        console.error('Analytics error:', error);
    }
}

// Track button clicks
export function trackButtonClick(buttonName, location) {
    try {
        logEvent(analytics, 'button_click', {
            button_name: buttonName,
            location: location
        });
        console.log(`📊 Analytics: Button clicked - ${buttonName}`);
    } catch (error) {
        console.error('Analytics error:', error);
    }
}

// Track feature usage
export function trackFeatureUsage(featureName, action) {
    try {
        logEvent(analytics, 'feature_usage', {
            feature_name: featureName,
            action: action
        });
        console.log(`📊 Analytics: Feature used - ${featureName}: ${action}`);
    } catch (error) {
        console.error('Analytics error:', error);
    }
}

// Track errors
export function trackError(errorType, errorMessage, location) {
    try {
        logEvent(analytics, 'error_occurred', {
            error_type: errorType,
            error_message: errorMessage,
            location: location
        });
        console.log(`📊 Analytics: Error tracked - ${errorType}`);
    } catch (error) {
        console.error('Analytics error:', error);
    }
}

// Track user engagement time
export function trackEngagement(pageName, timeSpent) {
    try {
        logEvent(analytics, 'user_engagement', {
            page_name: pageName,
            engagement_time_msec: timeSpent
        });
        console.log(`📊 Analytics: Engagement tracked - ${pageName}: ${timeSpent}ms`);
    } catch (error) {
        console.error('Analytics error:', error);
    }
}

// Auto-track page views on load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        const pageName = document.title || 'Unknown Page';
        trackPageView(pageName);
    });
} else {
    const pageName = document.title || 'Unknown Page';
    trackPageView(pageName);
}

// Track engagement time
let pageLoadTime = Date.now();
window.addEventListener('beforeunload', () => {
    const timeSpent = Date.now() - pageLoadTime;
    const pageName = document.title || 'Unknown Page';
    trackEngagement(pageName, timeSpent);
});

console.log('✅ Analytics module loaded');
