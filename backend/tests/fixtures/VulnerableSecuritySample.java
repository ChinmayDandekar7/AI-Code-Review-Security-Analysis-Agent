import java.sql.*;
import java.io.*;
import java.security.MessageDigest;
import javax.xml.parsers.DocumentBuilderFactory;

public class UserService {
    private String apiKey = "sk-live-51H8xJ2eZvKYlo2CabcDEF123456";
    private String dbPassword = "changeme";

    public void findUser(Connection conn, String username) throws SQLException {
        Statement stmt = conn.createStatement();
        ResultSet rs = stmt.executeQuery("SELECT * FROM users WHERE username = '" + username + "'");
    }

    public void findUserSafe(Connection conn, String username) throws SQLException {
        PreparedStatement stmt = conn.prepareStatement("SELECT * FROM users WHERE username = ?");
        stmt.setString(1, username);
        stmt.executeQuery();
    }

    public void backup(String filename) throws IOException {
        Runtime.getRuntime().exec("tar -czf backup.tar.gz " + filename);
    }

    public void backupSafe(String filename) throws IOException {
        ProcessBuilder pb = new ProcessBuilder("tar", "-czf", "backup.tar.gz", filename);
        pb.start();
    }

    public String hashPassword(String password) throws Exception {
        MessageDigest md = MessageDigest.getInstance("MD5");
        return md.digest(password.getBytes()).toString();
    }

    public Object loadData(byte[] data) throws Exception {
        ObjectInputStream ois = new ObjectInputStream(new ByteArrayInputStream(data));
        return ois.readObject();
    }

    public DocumentBuilderFactory getXmlFactory() {
        return DocumentBuilderFactory.newInstance();
    }

    public void writeGreeting(javax.servlet.http.HttpServletResponse response, String name) throws IOException {
        response.getWriter().println("<h1>Hello " + name + "</h1>");
    }

    public void writeGreetingSafe(javax.servlet.http.HttpServletResponse response, String name) throws IOException {
        response.getWriter().println("<h1>Welcome</h1>");
    }
}
