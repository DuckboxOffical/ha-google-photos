class GooglePhotosSlideshowCard extends HTMLElement {
  setConfig(config) {
    this.config = config;
    this.entity = config.entity || 'camera.google_photos';
    this.interval = config.interval || 10;
    this.transition = config.transition || 'fade';
    this.transitionDuration = config.transition_duration || 1000;
    this.showInfo = config.show_info !== false;
    this.fullscreen = config.fullscreen !== false;
    
    if (!this.content) {
      this.attachShadow({ mode: 'open' });
      this.content = document.createElement('div');
      this.content.className = 'google-photos-slideshow';
      this.shadowRoot.appendChild(this.content);
      
      const style = document.createElement('style');
      style.textContent = `
        .google-photos-slideshow {
          position: relative;
          width: 100%;
          height: 100%;
          overflow: hidden;
          background: #000;
        }
        .slide {
          position: absolute;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          object-fit: contain;
          opacity: 0;
          transition: opacity ${this.transitionDuration}ms ease-in-out;
        }
        .slide.active {
          opacity: 1;
        }
        .info {
          position: absolute;
          bottom: 0;
          left: 0;
          right: 0;
          background: linear-gradient(to top, rgba(0,0,0,0.7), transparent);
          color: white;
          padding: 20px;
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
          display: none;
        }
        .info.show {
          display: block;
        }
        .info-title {
          font-size: 18px;
          font-weight: 600;
          margin-bottom: 5px;
        }
        .info-subtitle {
          font-size: 14px;
          opacity: 0.9;
        }
      `;
      this.shadowRoot.appendChild(style);
    }
  }

  set hass(hass) {
    this._hass = hass;
    this.updateContent();
  }

  updateContent() {
    if (!this._hass) return;
    
    const state = this._hass.states[this.entity];
    if (!state) {
      this.content.innerHTML = '<div style="color: white; padding: 20px;">Entity not found: ' + this.entity + '</div>';
      return;
    }

    const photoUrl = state.attributes.photo_url;
    if (!photoUrl) {
      this.content.innerHTML = '<div style="color: white; padding: 20px;">No photo available</div>';
      return;
    }

    // Create or update slides
    let currentSlide = this.content.querySelector('.slide.active');
    if (!currentSlide) {
      currentSlide = document.createElement('img');
      currentSlide.className = 'slide active';
      this.content.appendChild(currentSlide);
    }

    // Update image source
    if (currentSlide.src !== photoUrl) {
      const newSlide = document.createElement('img');
      newSlide.className = 'slide';
      newSlide.src = photoUrl;
      newSlide.onload = () => {
        // Fade transition
        currentSlide.classList.remove('active');
        setTimeout(() => {
          this.content.removeChild(currentSlide);
        }, this.transitionDuration);
        newSlide.classList.add('active');
      };
      this.content.appendChild(newSlide);
    }

    // Update info
    if (this.showInfo) {
      let info = this.content.querySelector('.info');
      if (!info) {
        info = document.createElement('div');
        info.className = 'info show';
        this.content.appendChild(info);
      }
      
      const albumName = state.attributes.album_name || 'All Photos';
      const currentPhoto = state.attributes.current_photo || 0;
      const photoCount = state.attributes.photo_count || 0;
      
      info.innerHTML = `
        <div class="info-title">${albumName}</div>
        <div class="info-subtitle">Photo ${currentPhoto} of ${photoCount}</div>
      `;
    } else {
      const info = this.content.querySelector('.info');
      if (info) {
        info.classList.remove('show');
      }
    }
  }

  getCardSize() {
    return 3;
  }
}

customElements.define('google-photos-slideshow-card', GooglePhotosSlideshowCard);

