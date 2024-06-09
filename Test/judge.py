import aiohttp
import asyncio

url = "http://127.0.0.1:8004/api/v1/judge"

cpp_code = """
#include <iostream>
using namespace std;

int main(){
    string s;
    cin >> s;
    
    cout << "Hello, " << s << "!";
    return 0;
}
"""

c_code = """
#include <stdio.h>

int main(){
    char c[50]; scanf("%s", c);
    
    printf("Hello, %s!", c);
    return 0;
}
"""

py_code = """
print("Hello, {}!".format(input()))
"""

java_code = """
import java.util.*;

class Solution {
    public static void main(String[] args){
        Scanner sc = new Scanner(System.in);

        String name = sc.nextLine();
        System.out.print(String.format("Hello, %s!", name));
    }
}
"""

async def request(language, code):
    data = {
        "problem_id": 1,
        "time_limit": 1,
        "memory_limit": 64,
        "language": language,
        "code": code,
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as res:
            while True:
                d = await res.content.readline()
                if not d:
                    break
                print(d.decode(encoding="utf-8"))

async def main():
    tasks = [
        request("cpp", cpp_code),
        request("c", c_code),
        request("py", py_code),
        request("java", java_code),
    ]
    await asyncio.gather(*tasks)

asyncio.run(main())