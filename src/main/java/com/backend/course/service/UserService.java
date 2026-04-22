package com.backend.course.service;

import com.backend.course.controller.exeption.UserException;
import com.backend.course.model.User;
import com.backend.course.repository.PostRepository;
import com.backend.course.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@RequiredArgsConstructor
public class UserService {

    private final UserRepository userRepository;
    private final PostRepository postRepository;

    public List<User> getAllUsers() {
        List<User> users = userRepository.findAll();
        users.forEach(this::loadUserRelations);
        return users;
    }

    public User getUserById(String id) {
        Long userId = Long.parseLong(id);
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new UserException("User with ID %s not found".formatted(userId)));
        loadUserRelations(user);
        return user;
    }

    private void loadUserRelations(User user) {
        if (user != null) {
            user.setPosts(postRepository.findByAuthorId(user.getId()));
        }
    }

    public User saveUser(User user) {
        return userRepository.save(user);
    }

    public void deleteUser(String id) {
        Long userId = Long.parseLong(id);
        if (!userRepository.existsById(userId)) {
            throw new UserException("User with ID %s not found".formatted(userId));
        }
        userRepository.deleteById(userId);
    }

    public User updateUser(String id, User user) {
        Long userId = Long.parseLong(id);
        User existing = userRepository.findById(userId)
                .orElseThrow(() -> new UserException("User with ID %s not found".formatted(userId)));

        existing.setNickname(user.getNickname());
        existing.setEmail(user.getEmail());

        return userRepository.save(existing);
    }
}
