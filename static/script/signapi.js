
//이름 형식 한글만 입력함수
function check_name(asValue) {
    const regname = /^(?=.*[가-힣])[가-힣]{2,}$/;
    return regname.test(asValue);
}

//아이디 형식 함수
function check_id(asValue) {
    const regid = /^(?=.*[a-zA-Z])[-a-zA-Z0-9_.]{2,10}$/;
    return regid.test(asValue);
}

// 회원가입 함수
async function handleSignup() {

    const signupData = {
        username: document.getElementById("username").value,
        userid: document.getElementById("userid").value,
        password: document.getElementById("userpw").value
    }
    const repass = document.getElementById("repass").value
    const uid = signupData['userid']
    const uname = signupData['username']
    const upassword = signupData['password']

    //정규표현식 비밀번호 8자리 대소문자, 특수문자포함
    const regExp = /^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$/;

    //빈칸, 형식X, 일때 알림창
    if (uname == "") {
        alert('이름을 입력해주세요.')
        $('#username').focus()
        return;
    }
    if (!check_name(uname)) {
        $('#help-uname').text('이름은 한글로 2자이상 입력')
        $('#username').focus()
        $('#username').val('')
        return;
    }
    if (uid == "") {
        alert('아이디를 입력해주세요.')
        $('#userid').focus()
        return;
    }
    if (!check_id(uid)) {
        $('#help-uid').text('영문/숫자/특수문자(._-)가능. 2-10자 입력')
        $('#userid').focus()
        $('#userid').val('')
        return;
    }
    if (upassword == "") {
        alert('비밀번호를 입력해주세요.')
        $('#userpw').focus()
        return;
    }
    if (!upassword.match(regExp)) {
        alert('비밀번호는 최소8자리 대소문자,특수문자 포함 입력해주세요.')
        $('#help-upw').text('비밀번호는 최소8자리 대소문자,특수문자 포함')
        $('#userpw').focus()
        $('#userpw').val('')
        return;
    }
    if (upassword !== repass) {
        alert('비밀번호가 일치하지 않습니다.')
        $('#help-pw-same').text('비밀번호를 다시 확인해주세요')
        $('#repass').focus()
        $('#repass').val('')


        return;
    }


    const response = await fetch('/api/signup', {
        method: 'POST',
        body: JSON.stringify(signupData)
    }
    )
    response_json = await response.json()
    console.log(response_json)



    if (response_json["result"] == "success") {
        window.alert(response_json["msg"])
        window.location.replace('/login');
    } else {
        window.alert(response_json["msg"])
        $('#userid').focus()
        $('#userid').val('')
        return;
    }
}

//  //발급받은 키 중 javascript키를 사용해준다.
//
// // 카카오 로그인 함수
//
// // console.log(Kakao.isInitialized()); // sdk초기화여부판단
//
// function kakaoLogin() {
//     window.Kakao.Auth.login({
//         scope: 'profile_nickname', //동의항목 페이지에 있는 개인정보 보호 테이블의 활성화된 ID값을 넣습니다.
//         success: function (response) {
//             localStorage.setItem('mytoken',response['access_token']) // 로그인 성공시 발급받은 토큰
//             console.log(response)
//             window.Kakao.API.request({  // 사용자 정보 가져오기
//                 url: '/v2/user/me',
//                 success: (res) => {
//                     console.log(res)
//                     const kakao_account = res.kakao_account;
//                     // console.log(kakao_account.profile["nickname"])
//                     const kakaoUserData = {
//                         "userid": res['id'],
//                         "username": kakao_account.profile["nickname"],
//                     }
//                     console.log(kakaoUserData)
//                     const response = fetch('/kakaologin', {
//                         method: 'POST',
//                         body: JSON.stringify(kakaoUserData)
//                     }
//                     )
//                     console.log(response)
//                     // localStorage.setItem('token', response['token'])
//                     // $.cookie('mytoken', response['token'], {path: '/'});
//                     window.location.replace('/main');
//
//                 }
//             });
//         },
//         fail: function (error) {
//             console.log(error);
//         }
//
//     });
// }

// function AddUser() {
//     $.ajax({
//         type: "POST",
//         url: "/kakaologin",
//         data: {
//             "userid": res['id'],
//             "username": kakao_account.profile["nickname"],
//         },
//         success: function (response) {
//             if (response['result'] == 'success') {
//                 alert('로그인 성공!')
//                 window.location.replace('/main');
//             }
//         }
//     })
// }
Kakao.init('ff16324da325a78de3968519e1701949');
let kakao = "https://kauth.kakao.com/oauth/authorize"
window.onload = ()=> {
    document.getElementById("K-auth").href=`${kakao}?client_id=d03317eabc78cb691cfc7a028d417342&redirect_uri=http://127.0.0.1:5000/redirect&response_type=code`
}
    //로그인 함수
    async function handleLogin() {
        const loginData = {
            userid: document.getElementById("userid").value,
            password: document.getElementById("userpw").value
        }

        const response = await fetch('/api/login', {
                method: 'POST',
                body: JSON.stringify(loginData)
            }
        )
        response_json = await response.json()

        localStorage.setItem("token", response_json.token)

        if (response_json["result"] == "success") {
            $.cookie('mytoken', response_json.token, {path: '/'});
            window.location.replace('/main');
        } else {
            alert(response_json["msg"])
            $('#userid').focus()
            return;
        }
    }

//카카오로그아웃
function kakaoout() {
    if (Kakao.Auth.getAccessToken()) {
        Kakao.API.request({
            url: '/v1/user/unlink',
            success: function (response) {
                console.log(response)
                alert("카카오로그아웃")
            },
            fail: function (error) {
                console.log(error)
            },
        })
        Kakao.Auth.setAccessToken(undefined)
    }
}
function kakaoLogout() {
    if (!Kakao.Auth.getAccessToken()) {
      alert('Not logged in.')
      return
    }
    Kakao.Auth.logout(function() {
      alert('logout ok\naccess token -> ' + Kakao.Auth.getAccessToken())
    })
  }


function logout() {
    localStorage.removeItem("token")
    $.removeCookie('mytoken');
    window.location.replace('/main');
}


// 유저 이름, 포인트 불러오는 함수
async function getUserInfo() {
    const response = await fetch('/getuserinfo', {
        headers: {
            'Authorization': localStorage.getItem("token")
        }
    }
    )
    if (response.status == 200) {
        response_json = await response.json()
        return [response_json.name, response_json.point]
    }
    else {
        return null
    }
}
