
//featured projects
document.addEventListener('DOMContentLoaded', function() {
  var carousel = document.querySelector('#carouselProjects');
  var carouselInstance = new bootstrap.Carousel(carousel, {
    interval: 5000, // Adjust interval as needed (in milliseconds)
    pause: 'hover', // Pause on mouse hover
    wrap: true // Enable wrap-around navigation
  });
});


//Hero SECTION
    document.addEventListener('DOMContentLoaded', function () {
    const images = document.querySelectorAll('.hero-image');
    let currentImageIndex = 0;

    function swapImages() {
      images[currentImageIndex].classList.remove('active');
      currentImageIndex = (currentImageIndex + 1) % images.length;
      images[currentImageIndex].classList.add('active');
    }

    setInterval(swapImages, 5000); // Change image every 5 seconds
  });

