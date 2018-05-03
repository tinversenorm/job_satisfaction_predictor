Array.from(document.getElementsByClassName('yn')).forEach(ynText => {
    var form = ynText.parentElement.parentElement.children;
    var hiddenform = form[form.length - 1];

    ynText.addEventListener('click', () => {
        var currVal = 'yes' === ynText.attributes.data.value ? 1 : 0;
        hiddenform.value = currVal;
        ynText.classList.add('selected');
        ynText.parentElement.children[currVal].classList.remove('selected');
        console.log(ynText.classList)
    });
});
