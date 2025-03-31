// Funcionalidad para los popups
document.addEventListener('DOMContentLoaded', function() {
    // Popups de usuario
    const streakBtn = document.getElementById('streak-btn');
    const streakPopup = document.getElementById('streak-popup');
    const profileBtn = document.getElementById('profile-btn');
    const profilePopup = document.getElementById('profile-popup');
  
    const isHovering = (el) => el.matches(':hover');
  
    const handleHover = (button, popup) => {
      button.addEventListener('mouseenter', () => {
        popup.classList.add('active');
      });
      
      button.addEventListener('mouseleave', () => {
        setTimeout(() => {
          if (!isHovering(popup)) popup.classList.remove('active');
        }, 200);
      });
      
      popup.addEventListener('mouseenter', () => {
        popup.classList.add('active');
      });
      
      popup.addEventListener('mouseleave', () => {
        popup.classList.remove('active');
      });
    };
  
    if (streakBtn && streakPopup) handleHover(streakBtn, streakPopup);
    if (profileBtn && profilePopup) handleHover(profileBtn, profilePopup);
  
    // Configurar todos los carruseles
    document.querySelectorAll('.carousel-container').forEach(container => {
      const carousel = container.querySelector('.carousel-wrapper');
      const leftBtn = container.querySelector('.carousel-btn.left');
      const rightBtn = container.querySelector('.carousel-btn.right');
      
      if (leftBtn && rightBtn && carousel) {
        // Mostrar siempre ambas flechas
        leftBtn.style.display = 'flex';
        rightBtn.style.display = 'flex';
        
        // Configurar el desplazamiento
        leftBtn.addEventListener('click', () => {
          carousel.scrollBy({ left: -220, behavior: 'smooth' });
        });
        
        rightBtn.addEventListener('click', () => {
          carousel.scrollBy({ left: 220, behavior: 'smooth' });
        });
        
        // Prevenir el corte al hacer hover
        [leftBtn, rightBtn].forEach(btn => {
          btn.addEventListener('mouseenter', () => {
            btn.style.zIndex = '20';
          });
          
          btn.addEventListener('mouseleave', () => {
            btn.style.zIndex = '10';
          });
        });
      }
    });
  
    // Efecto hover para las escuelas
    document.querySelectorAll('.escuela-icon').forEach(icon => {
      icon.addEventListener('mouseenter', () => {
        icon.querySelector('.circle').style.transform = 'scale(1.1)';
      });
      
      icon.addEventListener('mouseleave', () => {
        icon.querySelector('.circle').style.transform = 'scale(1)';
      });
    });
  
    // Precargar imágenes para evitar problemas de carga
    const images = document.querySelectorAll('.curso-img, .card-course img');
    images.forEach(img => {
      const src = img.getAttribute('src');
      if (src) {
        const tempImg = new Image();
        tempImg.src = src;
      }
    });
  });