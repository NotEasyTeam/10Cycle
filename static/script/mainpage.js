async function checkLogin() {
    const info = await getUserInfo();
    const username = document.getElementById("username")
    const name = document.getElementById("user-name")
    const userpoint = document.getElementById("userpoint")
    const point = document.getElementById("user-point")
    const loginoutButton = document.getElementById("loginout")
    if (info){
        username.innerText = info[0]
        userpoint.innerText = info[1]
        loginoutButton.innerText = "로그아웃"
        loginoutButton.setAttribute("onclick", "logout()")
    }else{
        name.innerText = ""
        point.innerText = ""
        loginoutButton.innerText = "로그인"
        loginoutButton.setAttribute("onclick", "location.href='/login'")
    }
}

getRecycleinfo();
checkLogin();
