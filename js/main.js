var checkbox = document.querySelector("input[name=dark-mode-toggle]");

function setTheme() {
    var theme = Cookies.get("theme");
    if (theme !== null) {
        document.documentElement.setAttribute('data-theme', Cookies.get("theme"));
        if (theme == "dark") {
            checkbox.checked = true;
        }
    }
}

function toggleTheme() {
    var theme;
    if (Cookies.get("theme") !== null) {
        theme = Cookies.get("theme");
        Cookies.remove("theme");
        theme = theme == "light" ? "dark" : "light";
        Cookies.set("theme", theme);
    } else {
        Cookies.set("theme", "dark");
        theme = "dark";
    }
    document.documentElement.setAttribute('data-theme', theme);
}

checkbox.addEventListener('change', function () {
    toggleTheme();
});


(function () {
    setTheme();
    setTimeout(function(){
        checkbox.style = "transition: all 500ms;";
    }, 500);
})();
