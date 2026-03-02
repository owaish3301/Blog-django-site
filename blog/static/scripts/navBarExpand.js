const navbar = document.querySelector("nav");
const navDropDown = document.querySelector(".nav-dropdown");
const navDropDownIcon = document.querySelector(".lucide-chevron-down");

function showDropDown(){
    const isDropDownActive = navbar.classList.contains("hidden");
    if(isDropDownActive){
        navbar.classList.remove("hidden");
        navDropDownIcon.style.transform = "rotate(180deg)"
    }
    else{
        navbar.classList.add("hidden");
        navDropDownIcon.style.transform = "rotate(0deg)"
    }
}


navDropDown.addEventListener('click',showDropDown)

// Highlight active nav link
const navLinks = document.querySelectorAll("a.nav-link");
const currentPath = window.location.pathname;

navLinks.forEach(link => {
    if (link.pathname === currentPath) {
        link.classList.add("active");
    }
});