package org.ultimania.sample;
import java.util.*;
/**
 * クラスのサンプル
 */
public class SampleClass {
  private static ResourceBundle rb = ResourceBundle.getBundle("message");
  public String getMessage(){
    return rb.getString("hello");
  }
}