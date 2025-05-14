// Theme Toggle and Mobile Menu Functionality
 document.addEventListener('DOMContentLoaded', () => {
   const themeToggle = document.getElementById('theme-toggle');
   const mobileThemeToggle = document.getElementById('mobile-theme-toggle');
   const themeIcon = document.getElementById('theme-icon-path');
   const htmlElement = document.documentElement;
   const mobileMenuToggle = document.getElementById('mobile-menu-toggle');
   const mobileMenuClose = document.getElementById('mobile-menu-close');
   const mobileMenu = document.getElementById('mobile-menu');
   
   // Function to set theme
   function setTheme(theme) {
     if (!theme) return;
     htmlElement?.setAttribute('data-theme', theme);
     localStorage.setItem('theme', theme);
     updateThemeIcon(theme);
   }
   
   // Function to update theme icon
   function updateThemeIcon(theme) {
     if (!themeIcon) return;
     if (theme === 'dark') {
       themeIcon.setAttribute('d', 'M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z');
     } else {
       themeIcon.setAttribute('d', 'M12 3v1m0 16v1m9-9h-1M4 12H3m3.343-5.657L5.636 5.636m12.728 12.728L18.364 18.364M12 7a5 5 0 110 10 5 5 0 010-10z');
     }
   }
   
   // Theme toggle event listeners
   if (themeToggle) {
     themeToggle.addEventListener('click', () => {
       const currentTheme = htmlElement?.getAttribute('data-theme');
       const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
       setTheme(newTheme);
     });
   }
   
   if (mobileThemeToggle) {
     mobileThemeToggle.addEventListener('click', () => {
       const currentTheme = htmlElement?.getAttribute('data-theme');
       const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
       setTheme(newTheme);
     });
   }
   
   // Mobile menu toggle
   if (mobileMenuToggle && mobileMenu) {
     mobileMenuToggle.addEventListener('click', () => {
       mobileMenu.classList.remove('hidden');
       setTimeout(() => {
         mobileMenu.querySelector('div')?.classList.remove('translate-x-full');
       }, 10);
     });
   }
   
   // Mobile menu close
   if (mobileMenuClose && mobileMenu) {
     mobileMenuClose.addEventListener('click', () => {
       mobileMenu.querySelector('div')?.classList.add('translate-x-full');
       setTimeout(() => {
         mobileMenu.classList.add('hidden');
       }, 300);
     });
   }
   
   // Initialize theme from localStorage or default
   const savedTheme = localStorage.getItem('theme') || 'light';
   setTheme(savedTheme);
   
   // Counter Animation
   const counter = document.getElementById('downloadCounter');
   const target = 5000; // Set your target number
   let current = 0;
   
   const updateCounter = () => {
     if (!counter) return;
     const increment = target / 100;
     if (current < target) {
       current += increment;
       counter.textContent = Math.ceil(current).toLocaleString();
       requestAnimationFrame(updateCounter);
     } else {
       counter.textContent = target.toLocaleString();
     }
   };
   
   // Start counter animation when element is in viewport
   const observer = new IntersectionObserver((entries) => {
     entries.forEach(entry => {
       if (entry.isIntersecting && counter) {
         updateCounter();
         observer.unobserve(entry.target);
       }
     });
   });
   
   if (counter) {
     observer.observe(counter);
   }
   
    // Contact Form Handling
    const contactForm = document.getElementById('contactForm');
    const contactFormAlert = document.getElementById('formAlert');
    const contactAlertMessage = document.getElementById('alertMessage');
    
    if (contactForm) {
        console.log('Contact form found, setting up event listener');
        contactForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            console.log('Contact form submitted');
            
            // Get form data
            const formData = {
                name: contactForm.name.value,
                email: contactForm.email.value,
                subject: contactForm.subject.value,
                message: contactForm.message.value
            };
            console.log('Form data:', formData);
            
            try {
                console.log('Sending contact form data to server...');
                const response = await fetch('/api/contact', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(formData)
                });
                
                const data = await response.json();
                console.log('Server response:', data);
                
                // Show alert
                contactFormAlert.classList.remove('hidden');
                
                if (response.ok) {
                    // Success
                    console.log('Contact form submission successful');
                    contactFormAlert.querySelector('.alert').classList.remove('alert-error');
                    contactFormAlert.querySelector('.alert').classList.add('alert-success');
                    contactAlertMessage.textContent = data.message;
                    contactForm.reset();
                } else {
                    // Error
                    console.log('Contact form submission failed:', data.error);
                    contactFormAlert.querySelector('.alert').classList.remove('alert-success');
                    contactFormAlert.querySelector('.alert').classList.add('alert-error');
                    contactAlertMessage.textContent = data.error;
                }
                
            } catch (error) {
                console.error('Error submitting contact form:', error);
                contactFormAlert.classList.remove('hidden');
                contactFormAlert.querySelector('.alert').classList.remove('alert-success');
                contactFormAlert.querySelector('.alert').classList.add('alert-error');
                contactAlertMessage.textContent = 'An error occurred. Please try again later.';
            }
        });
    } else {
        console.warn('Contact form not found in the DOM');
    }
    
    // Newsletter Form Handling
    const newsletterForm = document.querySelector('.newsletter-form');
    const newsletterAlert = document.getElementById('newsletterAlert');
    
    if (newsletterForm) {
        console.log('Newsletter form found, setting up event listener');
        newsletterForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            console.log('Newsletter form submitted');
            
            const emailInput = newsletterForm.querySelector('input[type="email"]');
            const email = emailInput.value;
            console.log('Newsletter email:', email);
            
            try {
                console.log('Sending newsletter subscription to server...');
                const response = await fetch('/api/newsletter', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ email })
                });
                
                const data = await response.json();
                console.log('Server response:', data);
                
                newsletterAlert.classList.remove('hidden');
                
                if (response.ok) {
                    console.log('Newsletter subscription successful');
                    newsletterAlert.className = 'alert alert-success mt-4';
                    newsletterAlert.textContent = data.message;
                    emailInput.value = '';
                } else {
                    console.log('Newsletter subscription failed:', data.error);
                    newsletterAlert.className = 'alert alert-error mt-4';
                    newsletterAlert.textContent = data.error;
                }
                
            } catch (error) {
                console.error('Error subscribing to newsletter:', error);
                newsletterAlert.classList.remove('hidden');
                newsletterAlert.className = 'alert alert-error mt-4';
                newsletterAlert.textContent = 'An error occurred. Please try again later.';
            }
        });
    } else {
        console.warn('Newsletter form not found in the DOM');
    }
 });