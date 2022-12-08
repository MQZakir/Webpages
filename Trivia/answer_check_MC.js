// First question
// To start after loading DOM contents
document.addEventListener('DOMContentLoaded', function()
{
    // Correct answers
    let corrects = document.querySelector(".correct1");
    corrects.addEventListener('click', function()
    {
        corrects.style.backgroundColor = 'green';
        document.querySelector('#feedback1').innerHTML = 'Correct: USA consists a total of 50 states. The last two states to join the union were Alaska and Hawaii. They both joined in 1959.';
    });

    // Incorrect answers
    let incorrects = document.querySelectorAll('.incorrect1');
    for (let i = 0; i < incorrects.length; i++)
        {
            incorrects[i].addEventListener('click', function()
            {
                incorrects[i].style.backgroundColor = 'red';
                document.querySelector('#feedback1').innerHTML = 'Incorrect!';
            });
        }
});


// Second question
// To start after loading DOM contents
document.addEventListener('DOMContentLoaded', function()
{
    // Correct answers
    let corrects = document.querySelector(".correct2");
    corrects.addEventListener('click', function()
    {
        corrects.style.backgroundColor = 'green';
        document.querySelector('#feedback2').innerHTML = 'Correct: Franklin D. Roosevelt spent the longest as President of USA. Roosevelt is the only American president to have served more than two terms.';
    });

    // Incorrect answers
    let incorrects = document.querySelectorAll('.incorrect2');
    for (let i = 0; i < incorrects.length; i++)
        {
            incorrects[i].addEventListener('click', function()
            {
                incorrects[i].style.backgroundColor = 'red';
                document.querySelector('#feedback2').innerHTML = 'Incorrect!';
            });
        }
});