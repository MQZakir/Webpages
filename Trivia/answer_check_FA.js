// First question
// To start after loading DOM contents
document.addEventListener('DOMContentLoaded', function()
{
    document.querySelector('#answer1').addEventListener('click', function()
    {
        let input = document.querySelector('#input1');

        // Change the input to lower case for easy check
        input_l = input.value.toLowerCase();

        // Correct answer
        if (input_l === 'none' || input_l === 'there isnt one' || input_l === 'there is no national language'
        || input_l === 'there is none' || input_l === 'there is no federal national language'
        || input_l === 'they dont have one' || input_l === 'we dont have one' || input_l === 'no language' || input_l === 'no')
        {
            input.style.backgroundColor = 'green';
            document.querySelector('#feedback3').innerHTML = 'Correct: The United States does not have an official language at the federal level, but the most commonly used language is English (specifically, American English), which is the de facto national language.';
        }

        // Incorrect answer
        else
        {
            input.style.backgroundColor = 'red';
            document.querySelector('#feedback3').innerHTML = 'Incorrect: The United States does not have an official language at the federal level, but the most commonly used language is English (specifically, American English), which is the de facto national language.';
        }
    });
});


// Second question
// To start after loading DOM contents
document.addEventListener('DOMContentLoaded', function()
{
    document.querySelector('#answer2').addEventListener('click', function()
    {
        let input2 = document.querySelector('#input2');

        // Change the input to lower case for easy check
        input_l2 = input2.value.toLowerCase();

        // Correct answer
        if (input_l2 === '10 cents')
        {
            input2.style.backgroundColor = 'green';
            document.querySelector('#feedback4').innerHTML = 'Correct: A dime is worth 10 cents. A quarter is worth 25 cents, while a nickel and penny are worth 5 cents and 1 cent respectively.';
        }

        // Incorrect answer
        else
        {
            input2.style.backgroundColor = 'red';
            document.querySelector('#feedback4').innerHTML = 'Incorrect: A dime is worth 10 cents. A quarter is worth 25 cents, while a nickel and penny are worth 5 cents and 1 cent respectively.';
        }
    });
});