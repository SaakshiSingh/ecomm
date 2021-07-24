function changeBG()
{
	const bg = document.querySelector("#header");
	var randomCount = (Math.floor(Math.random() * 2));
   // I changed your array to the literal notation. The literal notation is preferred.
   var images = ['diary2.jpg', 'diary.jpg'];

    bg.style.setProperty('background-image',"url(" + images[randomCount] + ")") ;
}

window.onload = changeBG;