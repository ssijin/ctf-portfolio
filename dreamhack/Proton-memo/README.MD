# Challenge: dreamhack - Proton Memo

## 문제 설명 & 접근
https://dreamhack.io/wargame/challenges/884
플래그를 얻기 위해서는 아래와 같이 설정된 secret 파일을 열람해 내용을 읽어야 하는 것을 알 수 있다.
```python
secret = Memo("secret", open("/flag", "r").read(), os.urandom(20).hex())
Memo.add_memo_to_collection(secret)
```
secret의 비밀번호를 알아내기는 무리이고 어떤 공격이 가능할까?


## 문제 풀이
step 1
* app.py를 보자. /new로 접근해 파일에 title, content, password를 설정하면 새로운 Memo 객체가 생성된다. 그리고 각 Memo 객체에 대해 수정할 수 있는 기능이 들어있다. selected_option에는 title, content를 선택할 수 있게끔 되어있고 edit_data와 password를 입력받는다. 여기서 get_memo_with_auth_or_abort 함수로 검증하는데 해당 password가 기존 memo의 password와 일치하는지를 확인한다. 그리고 그 다음에 set_attr로 데이터의 변경을 반영해준다. 따라서 그냥 selected_option의 값을 바꾸고 secret_memo의 id를 알고 있다는 내용만으로 secret memo의 내용 열람은 불가능하다.
    ```python
    @app.route("/edit/<uuid:memo_id>", methods=["GET", "POST"])
    def edit_memo(memo_id: UUID):
        memo_id = str(memo_id)

        if request.method == "GET":
            return render_template("edit_memo.html", memo_id=memo_id)
        elif request.method == "POST":
            selected_option = request.form["selected_option"]
            edit_data = request.form["edit_data"]
            password = request.form["password"]

            memo = get_memo_with_auth_or_abort(memo_id, password)

            set_attr(memo, selected_option + ".data", edit_data)
            set_attr(memo, selected_option + ".edit_time", time.time())

            return redirect(url_for("index"))
            ```
step 2
다른 memo 객체를 생성할 수 있으니 해당 객체에 대해 /edit으로 접근해 get_memo_with_auth_or_abort를 만족시키고 그 다음에 set_attr을 이용해 다른 객체인 secret을 변경할 수 있지 않을까? 여기서 class pollution을 떠올렸다. set_attr 로직부터 확인해보자.
    ```python
    def set_attr(obj, prop, value):
    prop_chain = prop.split('.')
    cur_prop = prop_chain[0]
    if len(prop_chain) == 1:
        if isinstance(obj, dict):
            obj[cur_prop] = value
        else:
            setattr(obj, cur_prop, value)
    else:
        if isinstance(obj, dict):
            if  cur_prop in obj:
                next_obj = obj[cur_prop]
            else:
                next_obj = {}
                obj[cur_prop] = next_obj
        else:
            if hasattr(obj, cur_prop):
                next_obj = getattr(obj, cur_prop)
            else:
                next_obj = {}
                setattr(obj, cur_prop, next_obj)
        set_attr(next_obj, '.'.join(prop_chain[1:]), value)
    ```
    * 가장 일반적으로 접근해보자. title이 "attack", content가 "attack", password가 "1234"인 memo를 생성하고 /edit에서 selected_option을 "title"로 두고 edit_data에 "abcd", password를 "1234"를 입력해보자. 당연히 검증은 통과할 것이고 set_attr(memo, title.data, "attack")이 실행된다. 위 코드에 의해 next_obj=getattr(memo, title) => set_attr(memo.title, data, "abcd") => setattr(memo.title, data, "abcd")가 되어 해당 memo의 title이 바뀌는 것이다.
    * 이를 class pollution 관점에서 생각해보면 /edit에서 selected_option을 ```"__class__.collections[secret의 id].password"```로 두고 edit_data에 값을 넣으면, pollution이 일어나지 않을까? 아래는 module.py에 있는 class Memo 코드이다. collection에 memo가 생성될 때마다 추가하기 때문에 ```"__class__.collections[secret의 id]"```로 접근하면 secret 객체로 접근 가능할 것이다. 여기에 password 값까지 넣어두고 edit_data에 원하는 값을 넣어주면 password 변경이 가능하다.
        ```python
        class Memo:
        collections: Dict[str, Memo] = {}

        title: Title
        content: Content
        password: Password

        def __init__(self, title: str, content: str, password: str):
            self.id = str(uuid4())
            self.title = Title(title)
            self.content = Content(content)
            self.password = Password(password)

        def get_raw_title(self):
            return self.title

        def get_raw_content(self):
            return self.content

        def get_title(self):
            return self.title.get_title()

        def get_content(self):
            return self.content.get_content()

        def get_title_with_edit_time(self):
            return self.title.get_title_with_edit_time()

        def get_content_with_edit_time(self):
            return self.content.get_content_with_edit_time()

        def check_password(self, password):
            return self.password.check_password(password)

        @staticmethod
        def get_memo_by_id(memo_id: str) -> Memo | None:
            return Memo.collections[memo_id] if memo_id in Memo.collections.keys() else None

        @staticmethod
        def add_memo_to_collection(memo: Memo):
            Memo.collections[memo.id] = memo
    ```

* 주의할 점은 edit_data에 입력할 때 check_password가 sha256을 거치기 때문에 똑같이 암호화를 한 값을 넣어줘야 한다는 것이다. 가령 원하는 비밀번호가 "1234"라면 "1234"를 아래 hashlib.~를 돌려서 나온 값을 넣어줘야 무사히 검증을 통과하고 secret memo의 내용을 볼 수 있다.
    ```python
    class Password:
        data: str

        def __init__(self, data: str) -> None:
            self.data = hashlib.sha256(data.encode()).hexdigest()

        def check_password(self, password: str) -> bool:
            return self.data == hashlib.sha256(password.encode()).hexdigest()
    ```

## 결과
pollution을 이용해 secret memo의 비밀번호를 바꿔서 열람하면 플래그를 얻을 수 있다.
참고로 ```memo.__class__```로 접근해도 되고 ```memo.__class__.__init__.__globals__.Memo로 __init__``` 메서드의 glboal namespace에서 Memo를 찾는 식으로의 접근도 가능하다.