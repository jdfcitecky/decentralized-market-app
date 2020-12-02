// axios傳輸資料時的設定
const axiosConfig = {
    headers: {
        'x-csrf-token': csrf
    }
};
console.log(axiosConfig);

// 當登入表單送出時
$('#loginForm').submit(function (event) {
    // 防止表單重整行為
    event.preventDefault();
    const form = {
        email: $('#loginEmail').val(),
        password: $('#loginPassword').val(),
    };
    console.log('[登入]', form)
    console.log('[Email]', form.email)
    console.log('[Password]', form.password)
    // 前端登入
    firebase.auth().signInWithEmailAndPassword(
        form.email,
        form.password
    )
        // 登入成功
        .then(res => {
            console.log('[成功]', res)
            // 取得該員的登入成功驗證碼
            res.user.getIdToken()
                .then(idToken => {
                    console.log('[idToken]', idToken)
                    // 把idToken送到後端app.py
                    // axios.post('路徑', 資料{}, 設定{})
                    const data = {
                        id_token: idToken
                    }
                    axios.post('/api/login', data, axiosConfig)
                        // 成功
                        .then(res => {
                            console.log('[res]', res);
                            // 重整畫面
                            window.location.reload();
                        })
                        // 失敗
                        .catch(err => {
                            console.log('[err]', err);
                            alert('發生錯誤，請重新嘗試。')
                        })
                })
        })
        // 登入失敗
        .catch(err => {
            console.log('[失敗]', err)
            // 彈出視窗顯示錯誤
            alert(err.message)
        });
});

// 當註冊表單送出時
$('#signUpForm').submit(function (event) {
    event.preventDefault();
    const form = {
        email: $('#signUpEmail').val(),
        password: $('#signUpPassword').val(),
    };
    console.log('[註冊]', form);
    // 前端註冊
    firebase.auth().createUserWithEmailAndPassword(
        form.email,
        form.password
    )
        // 登入成功
        .then(res => {
            console.log('[成功]', res)
            // 取得該員的登入成功驗證碼
            res.user.getIdToken()
                .then(idToken => {
                    console.log('[idToken]', idToken)
                    // 把idToken送到後端app.py
                    // axios.post('路徑', 資料{}, 設定{})
                    const data = {
                        id_token: idToken
                    }
                    axios.post('/api/login', data, axiosConfig)
                        // 成功
                        .then(res => {
                            console.log('[res]', res);
                            // 重整畫面
                            window.location.reload();
                        })
                        // 失敗
                        .catch(err => {
                            console.log('[err]', err);
                            alert('發生錯誤，請重新嘗試。')
                        })
                })
        })
        // 登入失敗
        .catch(err => {
            console.log('[失敗]', err)
            // 彈出視窗顯示錯誤
            alert(err.message)
        });
});

$('#logoutBtn').click(function () {
    console.log('[登出]');
    // 呼叫登出API
    // axios.post('路徑', {}資料, {}設定)
    axios.post('/api/logout', {}, axiosConfig)
        // 成功
        .then(res => {
            console.log('[res]', res);
            // 轉跳到首頁
            window.location = '/';
        })
        // 失敗
        .catch(err => {
            console.log('[err]', err);
            alert('發生錯誤，請重新嘗試。')
        });
});