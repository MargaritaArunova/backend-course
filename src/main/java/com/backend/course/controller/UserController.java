package com.backend.course.controller;

import com.backend.course.model.User;
import com.backend.course.service.UserService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/users")
@RequiredArgsConstructor
public class UserController {

    private final UserService userService;

    @GetMapping
    public List<User> getUsers() {
        return userService.getAllUsers();
    }

    @GetMapping("/{id}")
    public User getUserById(@PathVariable String id) {
        return userService.getUserById(id);
    }

    @DeleteMapping("/{id}")
    public void deleteUser(@PathVariable String id) {
        userService.deleteUser(id);
    }

    @PostMapping
    public User saveUser(@RequestBody User client) {
        return userService.saveUser(client);
    }

    @PutMapping(value = "/{id}")
    public User updateUser(@PathVariable(required = false) String id, @RequestBody User user) {
        return userService.updateUser(id, user);
    }

}
