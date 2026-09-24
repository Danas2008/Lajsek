/*
 * Kompas putující po ose výstav.
 *
 * Každá timeline na stránce je samostatná: má vlastní štětec i vlastní
 * postup, takže se mezi kategoriemi nic nepřenáší ani neresetuje.
 *
 * Postup se počítá vůči středu okna — jakmile je čtenářův pohled u
 * začátku osy, štětec stojí nahoře; u konce osy dojede dolů:
 *
 *     postup = (scroll + výška okna / 2 − horní hrana osy) / výška osy
 *
 * Výsledek se ořízne do rozsahu 0–1, takže štětec nikdy neuteče mimo
 * svou osu. Pozice se nastavuje výhradně přes transform (žádné top ani
 * margin), aby prohlížeč nemusel přepočítávat layout.
 */
(function () {
    'use strict';

    var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
    if (reduceMotion.matches) {
        return;   // uživatel si pohyb nepřeje; osa i milníky fungují dál
    }

    var timelines = Array.prototype.slice.call(
        document.querySelectorAll('.timeline')
    ).map(function (element) {
        return { element: element, marker: element.querySelector('.timeline-marker') };
    }).filter(function (item) {
        return item.marker !== null;
    });

    if (!timelines.length || !('IntersectionObserver' in window)) {
        return;
    }

    var LINE_INSET = 14;   // osa začíná a končí 14 px od okrajů (viz style.css)
    var visible = [];      // jen osy, které jsou právě v okně
    var ticking = false;
    var listening = false;

    function place(item) {
        var box = item.element.getBoundingClientRect();
        var height = box.height;
        if (height <= 0) {
            return;
        }
        var reference = window.innerHeight / 2;
        var progress = (reference - box.top) / height;
        progress = Math.min(1, Math.max(0, progress));

        var travel = Math.max(0, height - LINE_INSET * 2);
        var y = LINE_INSET + progress * travel;

        item.marker.style.transform =
            'translate(-50%, -50%) translateY(' + y.toFixed(1) + 'px) rotate(-9deg)';
        item.marker.style.opacity = '1';
    }

    function update() {
        ticking = false;
        for (var i = 0; i < visible.length; i++) {
            place(visible[i]);
        }
    }

    function onScroll() {
        if (!ticking) {
            ticking = true;
            window.requestAnimationFrame(update);
        }
    }

    function setListening(shouldListen) {
        if (shouldListen === listening) {
            return;
        }
        listening = shouldListen;
        if (shouldListen) {
            window.addEventListener('scroll', onScroll, { passive: true });
            window.addEventListener('resize', onScroll, { passive: true });
            onScroll();
        } else {
            window.removeEventListener('scroll', onScroll);
            window.removeEventListener('resize', onScroll);
        }
    }

    // Scroll posloucháme jen tehdy, když je aspoň jedna osa v okně.
    var observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
            var item = timelines.filter(function (candidate) {
                return candidate.element === entry.target;
            })[0];
            if (!item) {
                return;
            }
            var index = visible.indexOf(item);
            if (entry.isIntersecting && index === -1) {
                visible.push(item);
                place(item);
            } else if (!entry.isIntersecting && index !== -1) {
                visible.splice(index, 1);
            }
        });
        setListening(visible.length > 0);
    }, { rootMargin: '120px 0px' });

    timelines.forEach(function (item) {
        observer.observe(item.element);
    });

    // Kdyby si uživatel omezení pohybu zapnul až za běhu.
    var stop = function () {
        if (reduceMotion.matches) {
            setListening(false);
            observer.disconnect();
            timelines.forEach(function (item) {
                item.marker.style.opacity = '0';
            });
        }
    };
    if (typeof reduceMotion.addEventListener === 'function') {
        reduceMotion.addEventListener('change', stop);
    }
}());
