import java.awt.*;
import java.awt.event.*;
import java.io.*;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import javax.swing.*;

abstract class Customer {
    private String name;
    private String id;
    private int units;

    public Customer(String name, String id, int units) {
        this.name = name;
        this.id = id;
        this.units = units;
    }

    public String getName() { return name; }
    public String getId() { return id; }
    public int getUnits() { return units; }

    public abstract double calculateBill();
}

class DomesticCustomer extends Customer {
    public DomesticCustomer(String name, String id, int units) {
        super(name, id, units);
    }

    @Override
    public double calculateBill() {
        int u = getUnits();
        if (u <= 100) return u * 1.20;
        else if (u <= 300) return 100 * 1.20 + (u - 100) * 2.00;
        else return 100 * 1.20 + 200 * 2.00 + (u - 300) * 3.00;
    }
}

class CommercialCustomer extends Customer {
    public CommercialCustomer(String name, String id, int units) {
        super(name, id, units);
    }

    @Override
    public double calculateBill() {
        int u = getUnits();
        if (u <= 100) return u * 2.00;
        else if (u <= 300) return 100 * 2.00 + (u - 100) * 3.00;
        else return 100 * 2.00 + 200 * 3.00 + (u - 300) * 4.00;
    }
}

class IndustrialCustomer extends Customer {
    public IndustrialCustomer(String name, String id, int units) {
        super(name, id, units);
    }

    @Override
    public double calculateBill() {
        int u = getUnits();
        if (u <= 100) return u * 3.50;
        else if (u <= 300) return 100 * 3.50 + (u - 100) * 5.00;
        else return 100 * 3.50 + 200 * 5.00 + (u - 300) * 6.00;
    }
}

public class ElectricityBillSystem extends JFrame implements ActionListener {

    private JTextField nameField, idField, unitField;
    private JComboBox<String> typeBox;
    private JTextArea outputArea;
    private JButton generateBtn, clearBtn, saveBtn, exitBtn;

    public ElectricityBillSystem() {
        setTitle(" Electricity Bill Management System");
        setSize(650, 600);
        setLayout(new BorderLayout(10, 10));
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setLocationRelativeTo(null);
        getContentPane().setBackground(new Color(240, 250, 255));

        JPanel inputPanel = new JPanel(new GridLayout(5, 2, 10, 10));
        inputPanel.setBorder(BorderFactory.createTitledBorder("Enter Customer Details"));
        inputPanel.setBackground(new Color(230, 245, 255));

        inputPanel.add(new JLabel("Customer Name:"));
        nameField = new JTextField();
        inputPanel.add(nameField);

        inputPanel.add(new JLabel("Customer ID:"));
        idField = new JTextField();
        inputPanel.add(idField);

        inputPanel.add(new JLabel("Units Consumed:"));
        unitField = new JTextField();
        inputPanel.add(unitField);

        inputPanel.add(new JLabel("Customer Type:"));
        String[] types = {"Domestic", "Commercial", "Industrial"};
        typeBox = new JComboBox<>(types);
        inputPanel.add(typeBox);

        outputArea = new JTextArea();
        outputArea.setBorder(BorderFactory.createTitledBorder("Bill Details"));
        outputArea.setFont(new Font("Consolas", Font.PLAIN, 14));
        outputArea.setEditable(false);
        JScrollPane scroll = new JScrollPane(outputArea);

        generateBtn = new JButton("Generate Bill");
        clearBtn = new JButton("Clear");
        saveBtn = new JButton("Save Bill");
        exitBtn = new JButton("Exit");

        Color btnColor = new Color(90, 150, 255);
        generateBtn.setBackground(btnColor);
        generateBtn.setForeground(Color.white);

        saveBtn.setBackground(new Color(70, 180, 90));
        saveBtn.setForeground(Color.white);

        clearBtn.setBackground(new Color(255, 160, 70));

        exitBtn.setBackground(new Color(220, 70, 70));
        exitBtn.setForeground(Color.white);

        JPanel buttonPanel = new JPanel(new GridLayout(1, 4, 10, 10));
        buttonPanel.add(generateBtn);
        buttonPanel.add(saveBtn);
        buttonPanel.add(clearBtn);
        buttonPanel.add(exitBtn);

        add(inputPanel, BorderLayout.NORTH);
        add(scroll, BorderLayout.CENTER);
        add(buttonPanel, BorderLayout.SOUTH);

        generateBtn.addActionListener(this);
        saveBtn.addActionListener(this);
        clearBtn.addActionListener(this);
        exitBtn.addActionListener(this);

        setVisible(true);
    }

    @Override
    public void actionPerformed(ActionEvent e) {
        if (e.getSource() == generateBtn) generateBill();
        if (e.getSource() == saveBtn) saveBill();
        if (e.getSource() == clearBtn) {
            nameField.setText("");
            idField.setText("");
            unitField.setText("");
            outputArea.setText("");
        }
        if (e.getSource() == exitBtn) {
            if (JOptionPane.showConfirmDialog(this, "Exit Application?", "Exit",
                    JOptionPane.YES_NO_OPTION) == JOptionPane.YES_OPTION) System.exit(0);
        }
    }

    private void generateBill() {
        String name = nameField.getText().trim();
        String id = idField.getText().trim();
        String type = (String) typeBox.getSelectedItem();
        int units;

        if (name.isEmpty() || id.isEmpty() || unitField.getText().isEmpty()) {
            JOptionPane.showMessageDialog(this, "Please fill all fields!");
            return;
        }

        try { units = Integer.parseInt(unitField.getText()); }
        catch (NumberFormatException ex) {
            JOptionPane.showMessageDialog(this, "Units must be a valid number!");
            return;
        }

        Customer customer = switch (type) {
            case "Domestic" -> new DomesticCustomer(name, id, units);
            case "Commercial" -> new CommercialCustomer(name, id, units);
            default -> new IndustrialCustomer(name, id, units);
        };

        double amount = customer.calculateBill();
        double tax = amount * 0.05;
        double total = amount + tax;
        String time = LocalDateTime.now().format(DateTimeFormatter.ofPattern("dd-MM-yyyy HH:mm:ss"));

        outputArea.setText("""
========= ELECTRICITY BILL =========
""");
        outputArea.append("Date & Time     : " + time + "\n");
        outputArea.append("Customer Name   : " + name + "\n");
        outputArea.append("Customer ID     : " + id + "\n");
        outputArea.append("Customer Type   : " + type + "\n");
        outputArea.append("Units Consumed  : " + units + " units\n");
        outputArea.append("------------------------------------\n");
        outputArea.append(String.format("Bill Amount     : ₹ %.2f\n", amount));
        outputArea.append(String.format("Tax (5%%)        : ₹ %.2f\n", tax));
        outputArea.append(String.format("Total Payable   : ₹ %.2f\n", total));
        outputArea.append("====================================\nThank you for using our service!\n");
    }

    private void saveBill() {
        if (outputArea.getText().isEmpty()) {
            JOptionPane.showMessageDialog(this, "Generate a bill first!");
            return;
        }

        try (FileWriter writer = new FileWriter("ElectricityBill_" + idField.getText() + ".txt")) {
            writer.write(outputArea.getText());
            JOptionPane.showMessageDialog(this, "Bill saved successfully!");
        } catch (IOException ex) {
            JOptionPane.showMessageDialog(this, "Error saving file!");
        }
    }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(ElectricityBillSystem::new);
    }
}
