function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const csrftoken = getCookie('csrftoken');

const question_items = document.getElementsByClassName('question-like-section')
console.log(question_items)
for (let item of question_items) {
    const [counter, btn] = item.children;
    btn.addEventListener('click', function () {

        const formData = new FormData();
        formData.append('question_id', btn.dataset.id);

        const request = new Request('/question_like/', {
            method: 'POST',
            body: formData,
            headers: {'X-CSRFToken': csrftoken},
        });
        fetch(request)
            .then((response) => response.json())
            .then((data) => {
                console.log({data});
                counter.innerHTML = data.count;
                btn.style.background = data.color;
            })
    });
}

const answer_items = document.getElementsByClassName('answer-like-section')
console.log(answer_items)
for (let item of answer_items) {
    const [counter, btn] = item.children;
    btn.addEventListener('click', function () {

        const formData = new FormData();
        formData.append('answer_id', btn.dataset.id);

        const request = new Request('/answer_like/', {
            method: 'POST',
            body: formData,
            headers: {'X-CSRFToken': csrftoken},
        });
        fetch(request)
            .then((response) => response.json())
            .then((data) => {
                console.log({data});
                counter.innerHTML = data.count;
                btn.style.background = data.color;
            })
    });
}

const correct_items = document.getElementsByClassName('form-check')
for (let item of correct_items) {
    let box = item.children[0];
    let btn = item.children[2];
    btn.addEventListener('click', function() {
        if (box.checked) {
            const formData = new FormData();
            formData.append('answer_id', btn.dataset.id);
            const request = new Request('/correct_answer/', {
                method: 'POST',
                body: formData,
                headers: {'X-CSRFToken': csrftoken},
            });
            fetch(request)
                .then((response) => response.json())
                .then((data) => {
                    console.log({data});
                    item.children[0].style.display = 'none';
                    item.children[1].style.display = 'none';
                    item.children[2].style.display = 'none';
                    item.children[3].textContent = 'Этот ответ был отмечен как правильный!'
            })
        }
    });
}