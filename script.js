document.addEventListener('DOMContentLoaded', () => {

    /* -------------------------------------------------------------------------- */
    /*                               Mobile Menu                                  */
    /* -------------------------------------------------------------------------- */
    const mobileBtn = document.querySelector('.mobile-menu-btn');
    const navLinks = document.querySelector('.nav-links');

    if (mobileBtn && navLinks) {
        mobileBtn.addEventListener('click', () => {
            navLinks.classList.toggle('active');

            // Toggle icon between menu and close
            const icon = mobileBtn.querySelector('ion-icon');
            if (navLinks.classList.contains('active')) {
                icon.setAttribute('name', 'close-outline');
            } else {
                icon.setAttribute('name', 'menu-outline');
            }
        });

        // Close menu when a link is clicked
        navLinks.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', () => {
                navLinks.classList.remove('active');
                const icon = mobileBtn.querySelector('ion-icon');
                icon.setAttribute('name', 'menu-outline');
            });
        });
    }

    /* -------------------------------------------------------------------------- */
    /*                           Scroll Animations                                */
    /* -------------------------------------------------------------------------- */
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1
    };

    const observer = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible-scroll');
                observer.unobserve(entry.target); // Only animate once
            }
        });
    }, observerOptions);

    // Select all elements that need to animate on scroll
    const scrollElements = document.querySelectorAll('.fade-in-on-scroll');
    scrollElements.forEach(el => {
        el.classList.add('hidden-scroll'); // Add initial hidden state
        observer.observe(el);
    });

    /* -------------------------------------------------------------------------- */
    /*                             Dynamic Pricing Logic                          */
    /* -------------------------------------------------------------------------- */
    const pricingData = {
        'jan': {
            std: {
                price: '₹699',
                features: [
                    'Rapid Revision Notes',
                    'Jan Attempt Formula Sheets',
                    'Mock Test Strategy',
                    'Basic Doubt Support'
                ]
            },
            elite: {
                price: '₹999',
                features: [
                    'Everything in Standard',
                    'Daily 1:1 Mentorship',
                    'Personalised Jan Schedule',
                    'Past Year Q-Solving Sessions',
                    'Score Booster Analysis'
                ]
            }
        },
        'april-boards': {
            std: {
                price: '₹699',
                features: [
                    'HEADING:JEE',
                    'April attempt Comeback Strategy',
                    'Live Sessions',
                    'Paper Attempting Strategies',
                    'Best and Self Tested Resources',
                    'Weekly Performance Analysis',
                    'Daily Query Resolution via WhatsApp groups',
                    'HEADING:CBSE BOARDS',
                    'Clear list of high-weightage, sure-shot chapters for each subject',
                    'How to revise NCERT smartly',
                    'Best way to practice PYQs & sample papers',
                    'How to write board-perfect answers',
                    'Time management for 3-hour paper strategy'
                ]
            },
            elite: {
                price: '₹999',
                features: [
                    'HEADING:JEE',
                    'Everything in Standard',
                    'One to One Calls by Ashir and Asees twice a week',
                    'Personalised Daily Targets',
                    'Formula Sheets and Notes',
                    '5 Super Relevant JEE Mock Tests designed by us',
                    'Special Motivational Sessions',
                    'HEADING:CBSE BOARDS',
                    'Everything in Standard',
                    'Daily mini-targets for consistent progress',
                    'Quick formula sheets',
                    'English Revision lectures designed by us',
                    'Board sample papers for each subject curated by us'
                ]
            }
        },
        'april': {
            std: {
                price: '₹499',
                features: [
                    'April attempt Comeback Strategy',
                    'Live Sessions',
                    'Paper Attempting Strategies',
                    'Best and Self Tested Resources',
                    'Weekly Performance Analysis',
                    'Daily Query Resolution via WhatsApp groups'
                ]
            },
            elite: {
                price: '₹699',
                features: [
                    'Everything in Standard',
                    'One to One Calls by Ashir and Asees twice a week',
                    'Personalised Daily Targets',
                    'Formula Sheets and Notes',
                    '5 Super Relevant Mock Tests designed by us',
                    'Special Motivational Sessions'
                ]
            }
        }
    };

    const categorySelect = document.getElementById('pricing-category');
    const stdPrice = document.getElementById('std-price');
    const stdFeatures = document.getElementById('std-features');
    const elitePrice = document.getElementById('elite-price');
    const eliteFeatures = document.getElementById('elite-features');

    if (categorySelect && pricingData) {
        const updatePricingDisplay = (category) => {
            const pricingGrid = document.querySelector('.pricing-grid');
            const janMessage = document.getElementById('jan-closed-message');

            if (category === 'jan') {
                if (pricingGrid) pricingGrid.style.display = 'none';
                if (janMessage) janMessage.style.display = 'block';
                return; // Stop further updates for Jan
            } else {
                if (pricingGrid) pricingGrid.style.display = 'grid'; // Revert to grid
                if (janMessage) janMessage.style.display = 'none';
            }

            // Rocket Icon Visibility Logic
            const rocketTrigger = document.getElementById('mentor-rocket-trigger');
            if (rocketTrigger) {
                if (category === 'april-boards') {
                    rocketTrigger.style.display = 'block';
                } else {
                    rocketTrigger.style.display = 'none';
                }
            }

            const data = pricingData[category];
            if (data) {
                // Animate change
                [stdPrice, stdFeatures, elitePrice, eliteFeatures].forEach(el => {
                    el.style.opacity = '0';
                    el.style.transform = 'translateY(10px)';
                });

                setTimeout(() => {
                    // Update Prices
                    stdPrice.textContent = data.std.price;
                    elitePrice.textContent = data.elite.price;

                    // Update Features (Helper function)
                    const updateList = (ul, features) => {
                        ul.innerHTML = features.map(feat => {
                            if (feat.startsWith('HEADING:')) {
                                return `<li class="feature-heading">${feat.replace('HEADING:', '')}</li>`;
                            }
                            return `<li><ion-icon name="checkmark-circle-outline"></ion-icon> ${feat.includes('Everything') ? `<strong>${feat}</strong>` : feat}</li>`;
                        }).join('');
                    };

                    updateList(stdFeatures, data.std.features);
                    updateList(eliteFeatures, data.elite.features);

                    // Fade in
                    [stdPrice, stdFeatures, elitePrice, eliteFeatures].forEach(el => {
                        el.style.opacity = '1';
                        el.style.transform = 'translateY(0)';
                    });
                }, 200);
            }
        };

        // Event Listener
        categorySelect.addEventListener('change', (e) => {
            updatePricingDisplay(e.target.value);
        });

        // Initialize state based on default value
        updatePricingDisplay(categorySelect.value);
    }

    /* -------------------------------------------------------------------------- */
    /*                         Rocket Launch Logic                                */
    /* -------------------------------------------------------------------------- */
    const rocketObserverOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.3 // Trigger when 30% visible
    };

    const rocketObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const rocket = entry.target.querySelector('.rocket-ship');
                if (rocket) {
                    rocket.classList.add('launched');
                    // Stop observing once launched?
                    // rocketObserver.unobserve(entry.target);
                    // Keep it to re-launch if they scroll away? User probably wants one-time or consistent.
                    // Let's keep it simple: add class.
                }
            } else {
                // Optional: Reset if they scroll away to re-trigger?
                // const rocket = entry.target.querySelector('.rocket-ship');
                // if (rocket) rocket.classList.remove('launched');
            }
        });
    }, rocketObserverOptions);

    const pricingSection = document.querySelector('.pricing-section');
    if (pricingSection) {
        rocketObserver.observe(pricingSection);
    }

    /* -------------------------------------------------------------------------- */
    /*                             Checkout Redirection                           */
    /* -------------------------------------------------------------------------- */

    // Function to handle redirection
    const redirectToCheckout = (planType) => {
        const categorySelect = document.getElementById('pricing-category');
        const category = categorySelect ? categorySelect.value : 'jan';
        window.location.href = `/checkout?plan=${planType}&category=${category}`;
    };

    // Attach listeners to "Choose Plan" buttons
    // Note: We need to select them specifically. 
    // The Standard Plan button
    // Listeners removed to allow AuthManager to handle them


    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            const btn = form.querySelector('button');
            const originalText = btn.textContent;
            btn.textContent = 'Enrolling...';
            btn.style.opacity = '0.7';

            // Collect form data
            const formData = {
                name: form.querySelector('input[type="text"]').value,
                phone: form.querySelector('input[type="tel"]').value,
                classGrade: form.querySelector('select').value
            };

            try {
                const response = await fetch('/api/submit-form', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(formData)
                });

                if (response.ok) {
                    alert('Success! Your details have been saved. We will contact you shortly.');
                    form.reset();
                } else {
                    alert('Something went wrong. Please try again.');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Connection error. Please ensure the server is running.');
            } finally {
                btn.textContent = originalText;
                btn.style.opacity = '1';
            }
        });
    }
});

/* -------------------------------------------------------------------------- */
/*                         Board Mentor Pop-out Logic                         */
/* -------------------------------------------------------------------------- */
const boardPopout = document.getElementById('board-mentor-popout');
const closePopoutBtn = document.querySelector('.close-popout');
const pricingSection = document.getElementById('pricing');
let popoutClosed = false; // Track if user manually closed it

if (boardPopout && pricingSection && categorySelect) {

    // Function to check visibility and constraints
    const checkPopoutVisibility = () => {
        if (popoutClosed) return;

        const isAprilBoards = categorySelect.value === 'april-boards';
        const rect = pricingSection.getBoundingClientRect();
        const isPricingVisible = (rect.top <= window.innerHeight * 0.7) && (rect.bottom >= window.innerHeight * 0.2);

        if (isAprilBoards && isPricingVisible) {
            boardPopout.classList.add('active');
        } else {
            boardPopout.classList.remove('active');
        }
    };

    // Scroll Listener
    window.addEventListener('scroll', checkPopoutVisibility);

    // Change Listener (Immediate check when dropdown changes)
    categorySelect.addEventListener('change', () => {
        // Reset closed state if switching TO april-boards explicitly? 
        // Maybe better not to annoy user if they closed it. 
        // unique UX choice: let's reset it if they switch back to it to show the feature.
        if (categorySelect.value === 'april-boards') {
            popoutClosed = false;
        }
        checkPopoutVisibility();
    });

    if (closePopoutBtn) {
        closePopoutBtn.addEventListener('click', () => {
            boardPopout.classList.remove('active');
            popoutClosed = true;
        });
    }
}

/* -------------------------------------------------------------------------- */
/*                        Mentor Rocket Modal Logic                           */
/* -------------------------------------------------------------------------- */
const rocketTrigger = document.getElementById('mentor-rocket-trigger');
const mentorModal = document.getElementById('mentor-modal');

if (rocketTrigger && mentorModal) {
    const closeModal = mentorModal.querySelector('.modal-close');

    // Open Modal
    rocketTrigger.addEventListener('click', (e) => {
        e.stopPropagation(); // Prevent bubbling
        mentorModal.classList.add('active');
        document.body.style.overflow = 'hidden'; // Prevent background scrolling
    });

    // Close Modal Function
    const closeMentorModal = () => {
        mentorModal.classList.remove('active');
        document.body.style.overflow = ''; // Restore scrolling
    };

    // Close on X button
    if (closeModal) {
        closeModal.addEventListener('click', closeMentorModal);
    }

    // Close on Outside Click
    mentorModal.addEventListener('click', (e) => {
        if (e.target === mentorModal) {
            closeMentorModal();
        }
    });

    // Close on Escape Key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && mentorModal.classList.contains('active')) {
            closeMentorModal();
        }
    });
}

/* -------------------------------------------------------------------------- */
/*                                 FAQ Logic                                  */
/* -------------------------------------------------------------------------- */
const faqQuestions = document.querySelectorAll('.faq-question');

faqQuestions.forEach(question => {
    question.addEventListener('click', () => {
        const item = question.parentNode;
        const answer = item.querySelector('.faq-answer');

        // Toggle current
        const isActive = item.classList.contains('active');

        if (!isActive) {
            item.classList.add('active');
            answer.style.maxHeight = answer.scrollHeight + "px";
        } else {
            item.classList.remove('active');
            answer.style.maxHeight = null;
        }
    });
});

/* -------------------------------------------------------------------------- */
/*                           Authentication Logic                             */
/* -------------------------------------------------------------------------- */

class RealAuthService {
    constructor() {
        this.currentUser = null;
    }

    async checkSession() {
        try {
            const res = await fetch('/api/user');
            const data = await res.json();
            if (data.authenticated) {
                this.currentUser = data.user;
                return this.currentUser;
            }
        } catch (e) {
            console.error('Session check failed', e);
        }
        this.currentUser = null;
        return null;
    }

    async signIn(identifier, password) {
        const response = await fetch('/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ identifier, password })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Login failed');
        }

        this.currentUser = data.user;
        return data.user;
    }

    async register(details) {
        const response = await fetch('/api/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(details)
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Registration failed');
        }

        this.currentUser = data.user;
        return data.user;
    }

    async signOut() {
        await fetch('/api/logout', { method: 'POST' });
        this.currentUser = null;
    }
}

class AuthManager {
    constructor() {
        this.authService = new RealAuthService();
        this.pendingPlan = null;

        this.elements = {
            modal: document.getElementById('auth-modal'),
            profileTrigger: document.getElementById('profile-trigger'),
            profileName: document.querySelector('.profile-text'),

            // Views
            views: {
                login: document.getElementById('auth-view-login'),
                register: document.getElementById('auth-view-register'),
                loading: document.getElementById('auth-view-loading')
            },

            // Login Elements
            loginIdentifier: document.getElementById('login-identifier'),
            loginPassword: document.getElementById('login-password'),
            loginBtn: document.getElementById('login-submit-btn'),

            // Register Elements
            regName: document.getElementById('reg-name'),
            regEmail: document.getElementById('reg-email'),
            regPhone: document.getElementById('reg-phone'),
            regPassword: document.getElementById('reg-password'),
            regBtn: document.getElementById('register-submit-btn'),

            // Links
            toRegister: document.getElementById('switch-to-register'),
            toLogin: document.getElementById('switch-to-login'),

            closeModal: document.getElementById('auth-modal-close')
        };

        this.init();
    }

    async init() {
        this.attachListeners();
        this.interceptPlanButtons();

        // Check for existing session
        const user = await this.authService.checkSession();
        if (user) {
            this.updateProfileUI();
        }
    }

    updateProfileUI() {
        if (!this.elements.profileName) return;

        const dropdownName = document.querySelector('.dropdown-user-name');

        if (this.authService.currentUser) {
            const firstName = this.authService.currentUser.name.split(' ')[0];
            this.elements.profileName.textContent = firstName;
            if (dropdownName) dropdownName.textContent = this.authService.currentUser.name;
        } else {
            this.elements.profileName.textContent = 'Guest';
            if (dropdownName) dropdownName.textContent = 'Guest';
        }
    }

    interceptPlanButtons() {
        // Standard Plan
        const stdBtn = document.querySelector('.pricing-card:not(.elite-card) .btn');
        if (stdBtn) {
            const newStdBtn = stdBtn.cloneNode(true);
            stdBtn.parentNode.replaceChild(newStdBtn, stdBtn);
            newStdBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.handlePlanSelection('std');
            });

            // Elite Plan
            const eliteBtn = document.querySelector('.elite-card .btn');
            if (eliteBtn) {
                const newEliteBtn = eliteBtn.cloneNode(true);
                eliteBtn.parentNode.replaceChild(newEliteBtn, eliteBtn);
                newEliteBtn.addEventListener('click', (e) => {
                    e.preventDefault();
                    this.handlePlanSelection('elite');
                });
            }
        }
    }

    handlePlanSelection(planType) {
        if (this.authService.currentUser) {
            this.proceedToCheckout(planType);
        } else {
            this.pendingPlan = planType;
            this.openModal('login');
        }
    }

    proceedToCheckout(planType) {
        const categorySelect = document.getElementById('pricing-category');
        const category = categorySelect ? categorySelect.value : 'jan';
        window.location.href = `/checkout?plan=${planType}&category=${category}`;
    }

    attachListeners() {
        // Modal & Profile
        if (this.elements.profileTrigger) {
            this.elements.profileTrigger.addEventListener('click', (e) => {
                e.stopPropagation(); // Prevent closing immediately
                if (!this.authService.currentUser) {
                    this.openModal('login');
                } else {
                    this.toggleProfileDropdown();
                }
            });
        }

        // Close Dropdown on Outside Click
        document.addEventListener('click', () => {
            this.closeProfileDropdown();
        });

        // Sign Out Action
        const signOutBtn = document.getElementById('action-sign-out');
        if (signOutBtn) {
            signOutBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.handleLogout();
            });
        }

        this.elements.closeModal?.addEventListener('click', () => this.closeModal());
        if (this.elements.modal) {
            this.elements.modal.addEventListener('click', (e) => {
                if (e.target === this.elements.modal) this.closeModal();
            });
        }

        // Switch Views
        this.elements.toRegister?.addEventListener('click', (e) => {
            e.preventDefault();
            this.switchView('register');
        });
        this.elements.toLogin?.addEventListener('click', (e) => {
            e.preventDefault();
            this.switchView('login');
        });

        // Submit Login
        this.elements.loginBtn?.addEventListener('click', () => this.handleLogin());

        // Submit Register
        this.elements.regBtn?.addEventListener('click', () => this.handleRegister());
    }

    toggleProfileDropdown() {
        const dropdown = document.getElementById('profile-dropdown');
        if (dropdown) {
            dropdown.classList.toggle('active');
        }
    }

    closeProfileDropdown() {
        const dropdown = document.getElementById('profile-dropdown');
        if (dropdown) {
            dropdown.classList.remove('active');
        }
    }

    async handleLogout() {
        await this.authService.signOut();
        window.location.reload();
    }

    openModal(viewName = 'login') {
        this.switchView(viewName);
        this.elements.modal.classList.add('active');
    }

    closeModal() {
        this.elements.modal.classList.remove('active');
    }

    switchView(viewName) {
        Object.values(this.elements.views).forEach(view => {
            if (view) view.classList.remove('active');
        });
        this.elements.views[viewName]?.classList.add('active');
    }

    async handleLogin() {
        const id = this.elements.loginIdentifier.value.trim();
        const pass = this.elements.loginPassword.value;

        if (!id || !pass) {
            alert('Please enter your email or phone and password');
            return;
        }

        this.switchView('loading');
        try {
            await this.authService.signIn(id, pass);
            this.onAuthSuccess();
        } catch (error) {
            alert(error.message);
            this.switchView('login');
        }
    }

    async handleRegister() {
        const name = this.elements.regName.value;
        const email = this.elements.regEmail.value;
        const phone = this.elements.regPhone.value;
        const pass = this.elements.regPassword.value;

        if (!name || !email || !phone || !pass) {
            alert('Please fill all fields');
            return;
        }

        this.switchView('loading');
        try {
            await this.authService.register({ name, email, phone, password: pass });
            this.onAuthSuccess();
        } catch (error) {
            alert(error.message);
            this.switchView('register');
        }
    }

    onAuthSuccess() {
        this.closeModal();
        this.updateProfileUI();
        if (this.pendingPlan) {
            this.proceedToCheckout(this.pendingPlan);
        }
    }
}

// Initialize Auth
new AuthManager();
