# Challenge: dreamhack - Pybrid

## 문제 설명 & 접근
https://dreamhack.io/wargame/challenges/1880

## 추가 학습
### Prototype Pollution
* 객체의 프로토타입을 공격자가 임의로 조작해 다른 모든 객체에도 영향을 미치게 하는 공격 기법이다.
* 보통 자바스크립트에서 발생하는 취약점이다.
    * 자바스크립트 객체는 프로토타입 기반 상속 구조를 가지고 모든 객체는 공통 최상위 객체 Object.prototype을 공유한다. 
* 파이썬에서는 자바스크립트처럼 직접적으로 일어나지 않지만 유사한 상황이 일어날 수 있다.
    * 파이썬 객체는 class 기반 상속으로 객체 속성이나 class 속성을 조작해 비슷한 효과를 낼 수 있다. (```__dict__```나 ```__class__```)
    * 자바스크립트처럼 프로토타입 체인을 직접 오염시키는 구조는 아니며, 공격자가 ```__class__``` 속성을 조작한다면 해당 class 자체가 오염되어 같은 클래스를 공유하는 모든 instance가 오염될 수 있다.


## 문제 풀이
* app.py를 보니 위에서부터 상속받아오는 것을 알 수 있고, 이중 principal은 특별히 command 메서드를 가지고 있다. command를 보면, 객체가 cmd 속성을 가지고 있을 때 이를 popen으로 실행 가능하다. 따라서 principal 객체에 cmd 속성으로 "cat /flag.txt"의 내용을 넣어줘야할듯하다.
    ```python
    class Student: 
        def __init__(self, name):
            self.name = name
            self.role = "student"

    class Teacher(Student): 
        def __init__(self, name):
            super().__init__(name)
            self.role = "teacher"

    class SubstituteTeacher(Teacher): 
        def __init__(self, name):
            super().__init__(name)
            self.role = "substitute_teacher"

    class Principal(Teacher): 
        def __init__(self, name):
            super().__init__(name)
            self.role = "principal"

        def command(self):
            command = self.cmd if hasattr(self, 'cmd') else 'echo Permission Denied'
            return f'{popen(command).read().strip()}'
    ```


* command를 호출하는 내용은 아래와 같다. 전역변수 principal을 설정하고 /execute에 접근하면 전역변수 principal로 command를 실행한다. 문제는 지금 전역변수에 cmd 속성이 없다는 것이다.
    ```python
    principal = Principal("principal")
    members = []
    members.append({"name":"admin", "role":"principal"})
    @app.route('/execute', methods=['GET'])
    def execute():
        return jsonify({"result": principal.command()})
    ```
* 따라서 속성을 설정해주는 함수 merge에서 취약점을 찾아봐야한다. /add_members에서 role이 "principal"인 memeber를 추가해 merge 함수를 실행할 수 있다. 다만, 새 멤버에 대해 merge가 실행되는 것이므로 전역객체 principal에 영향을 주려면 class pollution을 일으켜야 한다. 어떻게 할 수 있을까?
    ```python
    def merge(src, dst):
    for k, v in src.items():
        if hasattr(dst, '__getitem__'):
            if dst.get(k) and type(v) == dict:
                merge(v, dst.get(k))
            else:
                dst[k] = v
        elif hasattr(dst, k) and type(v) == dict:
            merge(v, getattr(dst, k))
        else:
            setattr(dst, k, v)
    ```

step 2
* merge 함수를 자세히 봐야 한다. merge(src, dst)는 src에 있는 key와 value를 재귀적으로 dst 객체 또는 딕셔너리 속성에 덮어씌운다는 것을 알 수 있다. 따라서 ```{"__class__": {"cmd": "cat /flag.txt"}}``` 와 같은 값을 보내면 elif hasattr(dst, k) and type(v) == dict:를 만족하면서 ```merge({"cmd": "cat /flag.txt"}, getattr(new_member, "__class__"))```가 호출된다. setattr(Principal, "cmd", "cat /flag.txt")이 실행되면서 Principal class에 cmd가 추가되는 것이다.
* setattr()이 사용자 입력 검증 없이 클래스의 속성을 덮어써 생긴 취약점이다.


## 결과
exploit.py에 익스플로잇 코드를 작성했다. /add_members에서 role을 principal로 직접 전달이 안되기 때문에 burp suite나 requests를 사용하는 것이 좋다. 코드를 실행하고 /execute에 접근하면 플래그를 볼 수 있다.
