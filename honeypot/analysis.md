# Honeypot Analysis
- Throught this exercise I was able to see the importance of honeypots and how they are useful in finding malicious actors. 
## Summary of Observed Attacks
- Repeated failed SSH login attempts
- Use of simple or default usernames such as `test`, `root`, and `admin`
- Short-lived connections that terminated quickly after failed authentication
- Attempts to issue basic commands after authentication prompts
## Notable Patterns
- **Brute-force behavior:**  
  Multiple authentication attempts were observed from the same source IP within a short time window, indicating brute-force or credential-stuffing behavior.

- **Minimal command usage:**  
  When commands were attempted, they were simple exploratory inputs such as `pwd`, `ls`, or `ls -a`.

- **Short session duration:**  
  Most connections lasted only a few seconds, consistent with automated attack tools rather than interactive users.

- **Realistic deception:**  
  The honeypot successfully mimicked a real SSH service, convincing attackers to interact and attempt authentication.

## Recommendations
- **Deploy honeypots continuously** to build a long-term profile of attacker behavior.
- **Add alerting mechanisms** for repeated failed login attempts or suspicious IP addresses.
- **Avoid exposing real SSH services** to untrusted networks; use honeypots instead for visibility.
- **Regularly analyze logs** to identify attack trends and potential blacklisting candidates.
- **Increase realism** by simulating additional shell commands, file systems, and responses to further engage attackers.
