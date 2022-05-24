
/* POST 요청 ajax 코드 */
function uploadRecycle() {
    // 고유 id let 함수로 정의
    let today = new Date().toISOString()
    let image = $('#chooseFile')[0].files[0]
    let form_data = new FormData()

    console.log(today, image)
    form_data.append("image_give", image)
    form_data.append("date_give", today)

    $.ajax({
        type: "POST",
        url: '/upload',
        data: form_data,
        cache: false,
        contentType: false,
        processData: false,
        headers: { 'Authorization': localStorage.getItem("token") },
        success: function (response) {
            alert(response['msg'])
            console.log(response['msg'])
            window.location.replace('/uploadedmain');
        }
    })
}

function getUserRecycle() {
    $.ajax({
        type: 'GET',
        url: '/getuploadimage',
        data: {},
        headers: { 'Authorization': localStorage.getItem("token") }, // 401에러 떴을때, 헤더에 토큰 
        success: function (response) {
            let image = response['img']
            console.log(image)

            let temp_html = `<img class="uploaded-img" src="../static/image/${image}">` //경로문제 해결해야 모든 사진이 불러와진다
            $('#uploaded-image-box').append(temp_html)
        }
    })
};





function getuserpaper() {
    $('#papergrid').empty()
    $.ajax({
        type: 'GET',
        url: '/getuserpaper',
        data: {},
        headers: { 'Authorization': localStorage.getItem("token") },
        success: function (response) {

            let rows = response['user_paper']
            for (let i = 0; i < rows.length; i++) {
                let image = rows[i]['image']
                let temp_html = `<div class="griditem" > 
                                    <img src = "./static/image/${image}">                    
                                 </div>`
                $('#papergrid').append(temp_html)
            }
        }
    })
}

function getusermetal() {
    $('#metalgrid').empty()
    $.ajax({
        type: 'GET',
        url: '/getusermetal',
        data: {},
        headers: { 'Authorization': localStorage.getItem("token") },
        success: function (response) {
            let rows = response['user_metal']
            for (let i = 0; i < rows.length; i++) {
                let image = rows[i]['image']
                let temp_html = `<div class="griditem" > 
                                    <img src = "./static/image/${image}">                    
                                 </div>`
                $('#metalgrid').append(temp_html)
            }
        }
    })
}

function getuserplastic() {
    $('#plasticgrid').empty()
    $.ajax({
        type: 'GET',
        url: '/getuserplastic',
        data: {},
        headers: { 'Authorization': localStorage.getItem("token") },
        success: function (response) {
            let rows = response['user_plastic']
            for (let i = 0; i < rows.length; i++) {
                let image = rows[i]['image']
                let temp_html = `<div class="griditem" > 
                                    <img src = "./static/image/${image}">                    
                                 </div>`
                $('#plasticgrid').append(temp_html)
            }
        }
    })
}

function getuserglass() {
    $('#glassgrid').empty()
    $.ajax({
        type: 'GET',
        url: '/getuserglass',
        data: {},
        headers: { 'Authorization': localStorage.getItem("token") },
        success: function (response) {
            let rows = response['user_glass']
            for (let i = 0; i < rows.length; i++) {
                let image = rows[i]['image']
                let temp_html = `<div class="griditem" > 
                                    <img src = "./static/image/${image}">                    
                                 </div>`
                $('#glassgrid').append(temp_html)
            }
        }
    })
}
