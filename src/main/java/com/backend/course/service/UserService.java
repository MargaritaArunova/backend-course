package com.backend.course.service;

import com.backend.course.exeption.NotFoundException;
import com.backend.course.model.User;
import com.backend.course.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@RequiredArgsConstructor
public class UserService {

    private final UserRepository userRepository;

    public List<User> getAllUsers() {
        return userRepository.findAll()
                .stream()
                .toList();
    }

    public User getUserById(String id) {
        Long userId = Long.parseLong(id);
        return userRepository.findById(userId)
                .orElseThrow(() -> new NotFoundException(User.class, userId));
    }

    public User saveUser(User user) {
        return userRepository.save(user);
    }

    public void deleteUser(String id) {
        Long userId = Long.parseLong(id);
        if (!userRepository.existsById(userId)) {
            throw new NotFoundException(User.class, userId);
        }
        userRepository.deleteById(userId);
    }

    public User updateUser(String id, User user) {
        Long userId = Long.parseLong(id);
        User existing = userRepository.findById(userId)
                .orElseThrow(() -> new NotFoundException(User.class, userId));

        existing.setNickname(user.getNickname());
        existing.setEmail(user.getEmail());

        return userRepository.save(existing);
    }
}
