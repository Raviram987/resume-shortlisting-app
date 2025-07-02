import * as kokomi from "https://esm.sh/kokomi.js";
import * as THREE from "https://esm.sh/three";
import gsap from "https://esm.sh/gsap";

class Sketch extends kokomi.Base {
  create() {
    this.renderer.setClearColor(new THREE.Color("#000"), 1);
    this.camera.position.set(0, 0, 16);

    const sumFormula = n => (n * (n + 1)) / 2;
    const isOdd = n => n % 2 === 1;

    const circleCount = 3;
    const unitCount = 4;

    const imageFilenames = [
      "1.jpeg", "2.jpeg", "3.jpeg", "4.jpeg", "5.jpeg", "6.jpeg", "7.jpeg",
      "8.jpeg", "9.jpeg", "10.jpeg", "11.jpeg", "12.jpeg", "13.jpeg", "14.jpeg", "15.jpeg"
    ];

    const total = imageFilenames.length;

    const am = new kokomi.AssetManager(this, imageFilenames.map((file, i) => ({
      name: `tex${i + 1}`,
      type: "texture",
      path: `/static/landing/images/${file}`
    })));

    am.on("ready", () => {
      document.querySelector(".loader-screen")?.remove();
      document.querySelector(".hero-dom").style.opacity = 1;

      const rings = [];
      const lines = [];

      for (let i = 0; i < circleCount; i++) {
        const c1 = sumFormula(i) * unitCount;
        const c2 = sumFormula(i + 1) * unitCount;
        const textures = Object.values(am.items).slice(c1, c2);

        const ring = new THREE.Group();
        this.scene.add(ring);
        rings.push(ring);

        textures.forEach((tex, j) => {
          const group = new THREE.Group();
          ring.add(group);
          lines.push(group);

          const desiredWidth = 1.8;
          const aspect = tex.image.height / tex.image.width;
          const geometry = new THREE.PlaneGeometry(desiredWidth, desiredWidth * aspect);

          const material = new THREE.MeshBasicMaterial({
            map: tex,
            transparent: true,
            opacity: 1 - (i * 0.25) // simulate distance blur by fading
          });
          material.map.anisotropy = 1;
          material.map.minFilter = THREE.LinearFilter;
          material.map.magFilter = THREE.LinearFilter;
          material.needsUpdate = true;

          const mesh = new THREE.Mesh(geometry, material);
          const radius = 6 * (i + 1);
          const angle = (j / (c2 - c1)) * Math.PI * 2;

          mesh.position.x = radius;
          mesh.rotation.z = -Math.PI / 2;
          group.rotation.z = angle;
          group.add(mesh);
        });
      }

      const scroller = new kokomi.WheelScroller();
      scroller.listenForScroll();

      const dragger = new kokomi.DragDetecter(this);
      dragger.detectDrag();
      dragger.on("drag", delta => {
        scroller.scroll.target -= (delta.x || delta.y) * 2;
      });

      this.update(() => {
        scroller.syncScroll();
        rings.forEach((ring, i) => {
          ring.rotation.z += 0.0025 * (isOdd(i) ? -1 : 1) * (1 + scroller.scroll.delta);
        });
      });

      gsap.to(".hero-dom", { opacity: 1, duration: 2 });
    });
  }
}

const sketch = new Sketch("#sketch");
sketch.create();
