# crm-students
CRM system that helps to manage sales in educational centers

### Example
<pre>
let responseData = fetch("/auth/login",
                         {method: "POST",
                         body: {"login": "username",
                                "password": "secret_password" }})
                        .then(response => response.json())

let token = `${responseData.token_type} ${responseData.token}             

fetch("/get_users",
      {method: "GET",
       headers: {
         "Authorization": token
      }
      });
</pre>

### Update user
Login is not updatable!

